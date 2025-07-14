import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Eye } from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'
import Chart from '../components/Chart'
import MetricCard from '../components/MetricCard'

const Dashboard = ({ selectedAssets }) => {
  const { t } = useLanguage()
  const [timeframe, setTimeframe] = useState('1D')
  const [loading, setLoading] = useState(false)
  const [marketData, setMarketData] = useState(null)

  useEffect(() => {
    // Simulate API call
    setLoading(true)
    
    setTimeout(() => {
      setMarketData({
        totalValue: 125430.50,
        change24h: 2.34,
        volume: 1250000,
        volatility: 15.2,
        topGainers: [
          { symbol: 'BTC', name: 'Bitcoin', change: 5.2, price: 45234.12 },
          { symbol: 'ETH', name: 'Ethereum', change: 3.8, price: 3456.78 },
          { symbol: 'SOL', name: 'Solana', change: 8.9, price: 98.45 }
        ],
        topLosers: [
          { symbol: 'ADA', name: 'Cardano', change: -2.1, price: 0.45 },
          { symbol: 'DOT', name: 'Polkadot', change: -1.8, price: 6.78 }
        ]
      })
      setLoading(false)
    }, 1000)
  }, [selectedAssets, timeframe])

  const timeframes = [
    { value: '1D', label: t('day') },
    { value: '7D', label: t('week') },
    { value: '30D', label: t('month') },
    { value: '3M', label: t('quarter') },
    { value: '1Y', label: t('year') }
  ]

  const mockChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [120000, 122000, 118000, 125000, 123000, 125430],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {t('dashboard')}
          </h1>
          <p className="text-gray-400">
            {t('marketOverview')} • {selectedAssets.length} {t('selectAssets')}
          </p>
        </div>
        
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`
                px-3 py-1 rounded-lg text-sm font-medium transition-colors
                ${timeframe === tf.value
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/10'
                }
              `}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title={t('totalValue')}
          value={marketData ? `$${marketData.totalValue.toLocaleString()}` : '-'}
          change={marketData ? marketData.change24h : 0}
          icon={DollarSign}
          color="blue"
        />
        <MetricCard
          title={t('volume')}
          value={marketData ? `$${(marketData.volume / 1000000).toFixed(1)}M` : '-'}
          change={5.2}
          icon={BarChart3}
          color="green"
        />
        <MetricCard
          title={t('volatility')}
          value={marketData ? `${marketData.volatility}%` : '-'}
          change={-1.8}
          icon={Activity}
          color="purple"
        />
        <MetricCard
          title={t('performance')}
          value={marketData ? `${marketData.change24h > 0 ? '+' : ''}${marketData.change24h}%` : '-'}
          change={marketData ? marketData.change24h : 0}
          icon={TrendingUp}
          color="orange"
        />
      </div>

      {/* Main Chart */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {t('priceAnalysis')}
          </h2>
          <div className="flex items-center space-x-2">
            <Eye className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-400">Live</span>
          </div>
        </div>
        
        {selectedAssets.length > 0 ? (
          <Chart data={mockChartData} type="line" />
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>{t('selectAssets')}</p>
            </div>
          </div>
        )}
      </div>

      {/* Top Gainers & Losers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
            Top Gainers
          </h3>
          <div className="space-y-3">
            {marketData?.topGainers.map((asset) => (
              <div key={asset.symbol} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-green-400">{asset.symbol}</span>
                  </div>
                  <div>
                    <p className="font-medium text-white">{asset.name}</p>
                    <p className="text-sm text-gray-400">${asset.price.toLocaleString()}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-green-400 font-semibold">+{asset.change}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Losers */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <TrendingDown className="h-5 w-5 mr-2 text-red-400" />
            Top Losers
          </h3>
          <div className="space-y-3">
            {marketData?.topLosers.map((asset) => (
              <div key={asset.symbol} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-red-400">{asset.symbol}</span>
                  </div>
                  <div>
                    <p className="font-medium text-white">{asset.name}</p>
                    <p className="text-sm text-gray-400">${asset.price.toLocaleString()}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-red-400 font-semibold">{asset.change}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
