import { useState } from 'react'
import { Menu, X, Globe, Settings, Download } from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'

const Navbar = ({ sidebarOpen, setSidebarOpen }) => {
  const { language, changeLanguage, t } = useLanguage()
  const [showLanguageMenu, setShowLanguageMenu] = useState(false)

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/5 border-b border-white/10">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side */}
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              {sidebarOpen ? (
                <X className="h-6 w-6 text-white" />
              ) : (
                <Menu className="h-6 w-6 text-white" />
              )}
            </button>
            
            <div className="ml-4 lg:ml-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                CryptoAnalyzer
              </h1>
              <p className="text-sm text-gray-400 hidden sm:block">
                {t('marketOverview')}
              </p>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-2">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center space-x-2"
              >
                <Globe className="h-5 w-5 text-gray-300" />
                <span className="text-sm text-gray-300 hidden sm:block">
                  {language.toUpperCase()}
                </span>
              </button>
              
              {showLanguageMenu && (
                <div className="absolute right-0 mt-2 w-32 bg-black/80 backdrop-blur-md rounded-lg shadow-lg border border-white/10 py-1 z-50">
                  <button
                    onClick={() => {
                      changeLanguage('en')
                      setShowLanguageMenu(false)
                    }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-white/10 transition-colors ${
                      language === 'en' ? 'text-blue-400' : 'text-gray-300'
                    }`}
                  >
                    English
                  </button>
                  <button
                    onClick={() => {
                      changeLanguage('es')
                      setShowLanguageMenu(false)
                    }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-white/10 transition-colors ${
                      language === 'es' ? 'text-blue-400' : 'text-gray-300'
                    }`}
                  >
                    Español
                  </button>
                </div>
              )}
            </div>

            {/* Export Button */}
            <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
              <Download className="h-5 w-5 text-gray-300" />
            </button>

            {/* Settings Button */}
            <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
              <Settings className="h-5 w-5 text-gray-300" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
