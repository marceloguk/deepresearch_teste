import { DeepResearchInterface } from './components/DeepResearchInterface'
import { ThemeProvider } from './components/theme-provider'
import './App.css'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="deep-research-theme">
      <div className="min-h-screen bg-background">
        <DeepResearchInterface />
      </div>
    </ThemeProvider>
  )
}

export default App
