import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  BarChart3, 
  TrendingUp, 
  GitBranch, 
  PieChart, 
  Bitcoin, 
  DollarSign, 
  Gem,
  BarChart2,
  ChevronDown,
  ChevronRight,
  Check
} from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'

const Sidebar = ({ open, setOpen, selectedAssets, setSelectedAssets }) => {
  const { t } = useLanguage()
  const [expandedSections, setExpandedSections] = useState({
    crypto: true,
    traditional: true,
    commodities: true,
    indices: true
  })

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const toggleAsset = (asset) => {
    setSelectedAssets(prev => 
      prev.includes(asset) 
        ? prev.filter(a => a !== asset)
        : [...prev, asset]
    )
  }

  const navigation = [
    { name: t('dashboard'), href: '/', icon: BarChart3 },
    { name: t('analysis'), href: '/analysis', icon: TrendingUp },
    { name: t('correlations'), href: '/correlations', icon: GitBranch },
    { name: t('portfolio'), href: '/portfolio', icon: PieChart },
  ]

  const assetCategories = [
    {
      id: 'crypto',
      name: t('cryptocurrencies'),
      icon: Bitcoin,
      assets: [
        { id: 'BTC', name: t('bitcoin'), color: 'text-crypto-bitcoin' },
        { id: 'ETH', name: t('ethereum'), color: 'text-crypto-ethereum' },
        { id: 'ADA', name: 'Cardano', color: 'text-blue-400' },
        { id: 'SOL', name: 'Solana', color: 'text-purple-400' },
        { id: 'DOT', name: 'Polkadot', color: 'text-pink-400' },
      ]
    },
    {
      id: 'traditional',
      name: t('traditionalMarkets'),
      icon: DollarSign,
      assets: [
        { id: 'SPY', name: t('sp500'), color: 'text-green-400' },
        { id: 'QQQ', name: t('nasdaq'), color: 'text-blue-400' },
        { id: 'VTI', name: 'VTI', color: 'text-indigo-400' },
        { id: 'VXUS', name: 'VXUS', color: 'text-cyan-400' },
      ]
    },
    {
      id: 'commodities',
      name: t('commodities'),
      icon: Gem,
      assets: [
        { id: 'GOLD', name: t('gold'), color: 'text-yellow-400' },
        { id: 'SILVER', name: 'Silver', color: 'text-gray-300' },
        { id: 'OIL', name: t('oil'), color: 'text-orange-400' },
        { id: 'COPPER', name: 'Copper', color: 'text-orange-600' },
      ]
    },
    {
      id: 'indices',
      name: t('indices'),
      icon: BarChart2,
      assets: [
        { id: 'DJI', name: 'Dow Jones', color: 'text-blue-500' },
        { id: 'FTSE', name: 'FTSE 100', color: 'text-red-400' },
        { id: 'DAX', name: 'DAX', color: 'text-yellow-500' },
        { id: 'NIKKEI', name: 'Nikkei 225', color: 'text-red-500' },
      ]
    }
  ]

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:fixed inset-y-0 left-0 z-50 w-64 
        backdrop-blur-xl bg-black/40 border-r border-white/10
        transform transition-transform duration-300 ease-in-out
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setOpen(false)}
                className={({ isActive }) => `
                  flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* Asset Selection */}
          <div className="px-4 py-6 border-t border-white/10">
            <h3 className="text-sm font-semibold text-gray-400 mb-4">
              {t('selectAssets')}
            </h3>
            
            <div className="space-y-3">
              {assetCategories.map((category) => (
                <div key={category.id} className="space-y-2">
                  <button
                    onClick={() => toggleSection(category.id)}
                    className="flex items-center w-full px-2 py-1 text-sm text-gray-300 hover:text-white transition-colors"
                  >
                    <category.icon className="mr-2 h-4 w-4" />
                    <span className="flex-1 text-left">{category.name}</span>
                    {expandedSections[category.id] ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                  
                  {expandedSections[category.id] && (
                    <div className="ml-6 space-y-1">
                      {category.assets.map((asset) => (
                        <button
                          key={asset.id}
                          onClick={() => toggleAsset(asset.id)}
                          className={`
                            flex items-center w-full px-2 py-1 text-xs rounded transition-colors
                            ${selectedAssets.includes(asset.id)
                              ? 'bg-blue-600/20 text-blue-400'
                              : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }
                          `}
                        >
                          <div className={`w-2 h-2 rounded-full mr-2 ${asset.color}`} />
                          <span className="flex-1 text-left">{asset.name}</span>
                          {selectedAssets.includes(asset.id) && (
                            <Check className="h-3 w-3" />
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Selected Assets Counter */}
          {selectedAssets.length > 0 && (
            <div className="px-4 py-3 border-t border-white/10">
              <div className="bg-blue-600/20 border border-blue-500/30 rounded-lg p-3">
                <p className="text-sm text-blue-400">
                  {selectedAssets.length} {selectedAssets.length === 1 ? 'asset' : 'assets'} selected
                </p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {selectedAssets.map((asset) => (
                    <span
                      key={asset}
                      className="inline-flex items-center px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded"
                    >
                      {asset}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default Sidebar
