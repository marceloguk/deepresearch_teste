import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Search, 
  Brain, 
  Globe, 
  Database, 
  Zap, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2,
  Settings,
  Info,
  ArrowRight
} from 'lucide-react'

import { apiClient } from '../lib/api'
import { ResearchResult, ResearchMode, ResearchModeInfo, ClarificationQuestion, ClarificationAnswer, ClarificationWithAnswers } from '../types/api'

export function DeepResearchInterface() {
  const [query, setQuery] = useState('')
  const [selectedMode, setSelectedMode] = useState<ResearchMode>(ResearchMode.DEEP_RESEARCH_O3)
  const [includeClarification, setIncludeClarification] = useState(true)
  const [includePromptRewriting, setIncludePromptRewriting] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ResearchResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [researchModes, setResearchModes] = useState<Record<string, ResearchModeInfo>>({})
  const [apiInfo, setApiInfo] = useState<any>(null)
  
  const [clarificationStep, setClarificationStep] = useState<'none' | 'questions' | 'completed'>('none')
  const [clarificationQuestions, setClarificationQuestions] = useState<ClarificationQuestion[]>([])
  const [clarificationAnswers, setClarificationAnswers] = useState<string[]>([])
  const [clarifiedIntent, setClarifiedIntent] = useState<string>('')

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const [modesData, infoData] = await Promise.all([
        apiClient.getResearchModes(),
        apiClient.getApiInfo()
      ])
      setResearchModes(modesData.modes)
      setApiInfo(infoData)
    } catch (err) {
      setError(`Failed to load initial data: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const handleStartClarification = async () => {
    if (!query.trim()) {
      setError('Por favor, digite uma consulta de pesquisa')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)
    setClarificationStep('none')

    try {
      if (includeClarification) {
        console.log('Calling clarifyIntent API...')
        const clarificationResult = await apiClient.clarifyIntent(query.trim())
        console.log('Clarification result:', clarificationResult)
        
        if (clarificationResult.questions && clarificationResult.questions.length > 0) {
          console.log('Setting clarification questions:', clarificationResult.questions)
          setClarificationQuestions(clarificationResult.questions)
          setClarifiedIntent(clarificationResult.clarified_intent)
          setClarificationAnswers(new Array(clarificationResult.questions.length).fill(''))
          setClarificationStep('questions')
          setIsLoading(false)
          return
        } else {
          console.log('No clarification questions returned, proceeding with research')
          setClarifiedIntent(clarificationResult.clarified_intent || query.trim())
        }
      } else {
        console.log('Clarification disabled, proceeding with research')
      }
      
      await proceedWithResearch()
    } catch (err) {
      console.error('Error in handleStartClarification:', err)
      setError(err instanceof Error ? err.message : 'Falha na clarificação')
      setIsLoading(false)
    }
  }

  const handleAnswerChange = (index: number, answer: string) => {
    const newAnswers = [...clarificationAnswers]
    newAnswers[index] = answer
    setClarificationAnswers(newAnswers)
  }

  const handleSubmitAnswers = async () => {
    setIsLoading(true)
    setClarificationStep('completed')
    
    try {
      await proceedWithResearch()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha na pesquisa')
      setIsLoading(false)
    }
  }

  const handleSkipClarification = async () => {
    setClarificationStep('none')
    setIsLoading(true)
    try {
      await proceedWithResearch()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha na pesquisa')
      setIsLoading(false)
    }
  }

  const proceedWithResearch = async () => {
    try {
      let rewrittenPrompt = query.trim()
      let promptRewriteResult = null

      if (includePromptRewriting) {
        if (clarificationStep === 'completed' && clarificationQuestions.length > 0) {
          const answers: ClarificationAnswer[] = clarificationAnswers.map((answer, index) => ({
            question_index: index,
            answer: answer
          }))

          const clarificationWithAnswers: ClarificationWithAnswers = {
            questions: clarificationQuestions,
            answers: answers,
            clarified_intent: clarifiedIntent
          }

          promptRewriteResult = await apiClient.rewritePromptWithAnswers(query.trim(), clarificationWithAnswers)
        } else {
          const clarificationWithAnswers: ClarificationWithAnswers = {
            questions: [],
            answers: [],
            clarified_intent: clarifiedIntent || query.trim()
          }

          promptRewriteResult = await apiClient.rewritePromptWithAnswers(query.trim(), clarificationWithAnswers)
        }
        rewrittenPrompt = promptRewriteResult.rewritten_prompt
      }

      const analysisRequest = {
        rewritten_prompt: rewrittenPrompt,
        mode: selectedMode,
        original_query: query.trim()
      }

      const result = await apiClient.conductAnalysisOnly(analysisRequest)
      
      if (clarificationQuestions.length > 0) {
        result.clarification = {
          questions: clarificationQuestions,
          clarified_intent: clarifiedIntent
        }
      }
      
      if (promptRewriteResult) {
        result.prompt_rewrite = promptRewriteResult
      }

      setResult(result)
    } finally {
      setIsLoading(false)
    }
  }

  const getModeIcon = (mode: ResearchMode) => {
    switch (mode) {
      case ResearchMode.DEEP_RESEARCH_O3:
      case ResearchMode.DEEP_RESEARCH_O4_MINI:
        return <Brain className="h-4 w-4" />
      case ResearchMode.WEBSEARCH_ONLY:
        return <Globe className="h-4 w-4" />
      case ResearchMode.MCP_ONLY:
        return <Database className="h-4 w-4" />
      case ResearchMode.WEBSEARCH_MCP:
        return <Zap className="h-4 w-4" />
      default:
        return <Search className="h-4 w-4" />
    }
  }

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'clarification':
        return <Info className="h-4 w-4" />
      case 'prompt_rewriting':
        return <Settings className="h-4 w-4" />
      case 'search':
        return <Search className="h-4 w-4" />
      case 'fetch':
        return <Database className="h-4 w-4" />
      case 'analysis':
        return <Brain className="h-4 w-4" />
      default:
        return <ArrowRight className="h-4 w-4" />
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">API de Pesquisa Profunda</h1>
        <p className="text-muted-foreground text-lg">
          Implementação completa das capacidades de Pesquisa Profunda da OpenAI com múltiplos modos de pesquisa
        </p>
        {apiInfo && (
          <div className="flex flex-wrap gap-2 mt-4">
            {apiInfo.features?.map((feature: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {feature}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Configuração da Pesquisa
              </CardTitle>
              <CardDescription>
                Configure os parâmetros e fluxo de trabalho da sua pesquisa profunda
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="query">Consulta de Pesquisa</Label>
                <Textarea
                  id="query"
                  placeholder="Digite sua pergunta ou tópico de pesquisa..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="mode">Modo de Pesquisa</Label>
                <Select value={selectedMode} onValueChange={(value) => setSelectedMode(value as ResearchMode)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o modo de pesquisa" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(researchModes).map(([key, mode]) => (
                      <SelectItem key={key} value={key}>
                        <div className="flex items-center gap-2">
                          {getModeIcon(key as ResearchMode)}
                          <span>{mode.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {researchModes[selectedMode] && (
                  <div className="text-sm text-muted-foreground mt-2">
                    <p>{researchModes[selectedMode].description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {researchModes[selectedMode].capabilities.map((cap, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {cap}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium">Fluxo de Trabalho de 3 Etapas</h4>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="clarification">Etapa de Clarificação</Label>
                    <p className="text-xs text-muted-foreground">
                      Usa gpt-4.1 para clarificar intenção e coletar contexto
                    </p>
                  </div>
                  <Switch
                    id="clarification"
                    checked={includeClarification}
                    onCheckedChange={setIncludeClarification}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="rewriting">Reescrita de Prompt</Label>
                    <p className="text-xs text-muted-foreground">
                      Usa gpt-4.1 para reescrever o prompt para melhor pesquisa
                    </p>
                  </div>
                  <Switch
                    id="rewriting"
                    checked={includePromptRewriting}
                    onCheckedChange={setIncludePromptRewriting}
                  />
                </div>
              </div>

              <Button 
                onClick={handleStartClarification} 
                disabled={isLoading || !query.trim()}
                className="w-full"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processando...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Iniciar Pesquisa Profunda
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          {clarificationStep === 'questions' && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Perguntas de Clarificação
                </CardTitle>
                <CardDescription>
                  Por favor, responda às seguintes perguntas para melhorar sua pesquisa:
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {clarificationQuestions.map((question, index) => (
                    <div key={index} className="space-y-2">
                      <Label htmlFor={`question-${index}`} className="font-medium">
                        {question.question}
                      </Label>
                      <p className="text-sm text-muted-foreground">{question.context}</p>
                      <Textarea
                        id={`question-${index}`}
                        value={clarificationAnswers[index]}
                        onChange={(e) => handleAnswerChange(index, e.target.value)}
                        placeholder="Digite sua resposta..."
                        className="min-h-[80px]"
                      />
                    </div>
                  ))}
                  <div className="flex gap-2 pt-4">
                    <Button 
                      onClick={handleSubmitAnswers}
                      disabled={isLoading || clarificationAnswers.some(answer => !answer.trim())}
                      className="flex-1"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processando...
                        </>
                      ) : (
                        'Continuar Pesquisa'
                      )}
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={handleSkipClarification}
                      disabled={isLoading}
                    >
                      Pular Clarificação
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {error && (
            <Alert className="mb-6" variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>Erro: {error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    Resultados da Pesquisa
                  </CardTitle>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {formatDuration(result.total_duration_ms)}
                  </div>
                </div>
                <CardDescription>
                  Query: "{result.query}" • Mode: {researchModes[result.mode]?.name || result.mode}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="analysis" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="analysis">Análise</TabsTrigger>
                    <TabsTrigger value="workflow">Fluxo</TabsTrigger>
                    <TabsTrigger value="sources">Fontes</TabsTrigger>
                    <TabsTrigger value="details">Detalhes</TabsTrigger>
                  </TabsList>

                  <TabsContent value="analysis" className="mt-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Análise Final</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ScrollArea className="h-[400px]">
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <pre className="whitespace-pre-wrap text-sm">
                              {result.final_analysis}
                            </pre>
                          </div>
                        </ScrollArea>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="workflow" className="mt-6">
                    <div className="space-y-4">
                      {result.steps.map((step, index) => (
                        <Card key={index}>
                          <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {getStepIcon(step.step_type)}
                                <CardTitle className="text-base capitalize">
                                  {step.step_type.replace('_', ' ')}
                                </CardTitle>
                              </div>
                              <Badge variant="outline">
                                {formatDuration(step.duration_ms)}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="text-sm space-y-2">
                              <div>
                                <strong>Input:</strong>
                                <pre className="text-xs mt-1 p-2 bg-muted rounded">
                                  {JSON.stringify(step.input_data, null, 2)}
                                </pre>
                              </div>
                              <div>
                                <strong>Output:</strong>
                                <pre className="text-xs mt-1 p-2 bg-muted rounded">
                                  {JSON.stringify(step.output_data, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="sources" className="mt-6">
                    <div className="space-y-6">
                      {result.search_results.length > 0 && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-lg">Resultados da Busca</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              {result.search_results.map((searchResult, index) => (
                                <div key={index} className="border rounded p-3">
                                  <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                      <h4 className="font-medium text-sm">{searchResult.title}</h4>
                                      <p className="text-xs text-muted-foreground mt-1">
                                        {searchResult.url}
                                      </p>
                                      <p className="text-sm mt-2">{searchResult.snippet}</p>
                                    </div>
                                    {searchResult.relevance_score && (
                                      <Badge variant="secondary" className="ml-2">
                                        {(searchResult.relevance_score * 100).toFixed(0)}%
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      )}

                      {result.fetch_results.length > 0 && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-lg">Conteúdo Obtido</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              {result.fetch_results.map((fetchResult, index) => (
                                <div key={index} className="border rounded p-3">
                                  <h4 className="font-medium text-sm mb-2">
                                    Documento: {fetchResult.id}
                                  </h4>
                                  <ScrollArea className="h-[200px]">
                                    <pre className="text-xs whitespace-pre-wrap">
                                      {fetchResult.content}
                                    </pre>
                                  </ScrollArea>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="details" className="mt-6">
                    <div className="space-y-4">
                      {result.clarification && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-lg">Clarificação</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              <div>
                                <strong>Intenção Clarificada:</strong>
                                <p className="text-sm mt-1">{result.clarification.clarified_intent}</p>
                              </div>
                              {result.clarification.questions.length > 0 && (
                                <div>
                                  <strong>Perguntas Geradas:</strong>
                                  <ul className="text-sm mt-1 space-y-1">
                                    {result.clarification.questions.map((q, index) => (
                                      <li key={index} className="border-l-2 border-muted pl-3">
                                        <strong>{q.question}</strong>
                                        <p className="text-muted-foreground">{q.context}</p>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      )}

                      {result.prompt_rewrite && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-lg">Reescrita de Prompt</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              <div>
                                <strong>Consulta Original:</strong>
                                <p className="text-sm mt-1 p-2 bg-muted rounded">
                                  {result.prompt_rewrite.original_query}
                                </p>
                              </div>
                              <div>
                                <strong>Prompt Reescrito:</strong>
                                <p className="text-sm mt-1 p-2 bg-muted rounded">
                                  {result.prompt_rewrite.rewritten_prompt}
                                </p>
                              </div>
                              <div>
                                <strong>Justificativa:</strong>
                                <p className="text-sm mt-1">{result.prompt_rewrite.reasoning}</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {!result && !error && !isLoading && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Search className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">Pronto para Pesquisa Profunda</h3>
                <p className="text-muted-foreground text-center max-w-md">
                  Digite sua consulta de pesquisa e selecione um modo para começar a análise abrangente usando as capacidades de Pesquisa Profunda da OpenAI.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
