import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Correlations from './pages/Correlations'
import Portfolio from './pages/Portfolio'
import { LanguageProvider } from './utils/LanguageContext'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedAssets, setSelectedAssets] = useState([])

  return (
    <LanguageProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-20">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
          </div>
          
          {/* Animated Background Shapes */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full opacity-10 blur-3xl animate-pulse-slow"></div>
            <div 
              className="absolute top-3/4 right-1/4 w-80 h-80 bg-blue-500 rounded-full opacity-10 blur-3xl animate-pulse-slow" 
              style={{ animationDelay: '1s' }}
            ></div>
            <div 
              className="absolute top-1/2 left-1/2 w-64 h-64 bg-pink-500 rounded-full opacity-10 blur-3xl animate-pulse-slow" 
              style={{ animationDelay: '2s' }}
            ></div>
          </div>

          {/* Main Layout */}
          <div className="relative z-10">
            <Navbar 
              sidebarOpen={sidebarOpen} 
              setSidebarOpen={setSidebarOpen} 
            />
            
            <div className="flex">
              <Sidebar 
                open={sidebarOpen} 
                setOpen={setSidebarOpen}
                selectedAssets={selectedAssets}
                setSelectedAssets={setSelectedAssets}
              />
              
              <main className="flex-1 p-6 ml-0 lg:ml-64 transition-all duration-300">
                <div className="max-w-7xl mx-auto">
                  <Routes>
                    <Route path="/" element={<Dashboard selectedAssets={selectedAssets} />} />
                    <Route path="/analysis" element={<Analysis selectedAssets={selectedAssets} />} />
                    <Route path="/correlations" element={<Correlations selectedAssets={selectedAssets} />} />
                    <Route path="/portfolio" element={<Portfolio selectedAssets={selectedAssets} />} />
                  </Routes>
                </div>
              </main>
            </div>
          </div>
        </div>
      </Router>
    </LanguageProvider>
  )
}

export default App