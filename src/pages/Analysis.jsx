import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Activity, Download } from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'
import Chart from '../components/Chart'
import MetricCard from '../components/MetricCard'

const Analysis = ({ selectedAssets }) => {
  const { t } = useLanguage()
  const [analysisType, setAnalysisType] = useState('price')
  const [timeframe, setTimeframe] = useState('30D')
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)

  useEffect(() => {
    if (selectedAssets.length > 0) {
      setLoading(true)
      
      // Simulate API call
      setTimeout(() => {
        setAnalysisData({
          priceData: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: selectedAssets.map((asset, index) => ({
              label: asset,
              data: [
                100 + Math.random() * 50,
                110 + Math.random() * 50,
                105 + Math.random() * 50,
                120 + Math.random() * 50,
                115 + Math.random() * 50,
                125 + Math.random() * 50
              ],
              borderColor: `hsl(${index * 60}, 70%, 50%)`,
              backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.1)`,
              fill: false,
              tension: 0.4
            }))
          },
          volumeData: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: selectedAssets.map((asset, index) => ({
              label: asset,
              data: [
                1000000 + Math.random() * 500000,
                1100000 + Math.random() * 500000,
                1050000 + Math.random() * 500000,
                1200000 + Math.random() * 500000,
                1150000 + Math.random() * 500000,
                1250000 + Math.random() * 500000
              ],
              backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.7)`,
              borderColor: `hsl(${index * 60}, 70%, 50%)`,
              borderWidth: 1
            }))
          },
          volatilityData: {
            labels: selectedAssets,
            datasets: [{
              label: 'Volatility (%)',
              data: selectedAssets.map(() => 10 + Math.random() * 30),
              backgroundColor: selectedAssets.map((_, index) => `hsla(${index * 60}, 70%, 50%, 0.7)`),
              borderColor: selectedAssets.map((_, index) => `hsl(${index * 60}, 70%, 50%)`),
              borderWidth: 1
            }]
          },
          metrics: {
            avgReturn: 12.5,
            sharpeRatio: 1.8,
            maxDrawdown: -15.2,
            correlation: 0.65
          }
        })
        setLoading(false)
      }, 1000)
    }
  }, [selectedAssets, timeframe])

  const analysisTypes = [
    { value: 'price', label: t('priceComparison'), icon: TrendingUp },
    { value: 'volume', label: t('volume'), icon: BarChart3 },
    { value: 'volatility', label: t('volatilityAnalysis'), icon: Activity }
  ]

  const timeframes = [
    { value: '7D', label: t('week') },
    { value: '30D', label: t('month') },
    { value: '3M', label: t('quarter') },
    { value: '1Y', label: t('year') }
  ]

  const getCurrentChartData = () => {
    if (!analysisData) return null
    
    switch (analysisType) {
      case 'price':
        return analysisData.priceData
      case 'volume':
        return analysisData.volumeData
      case 'volatility':
        return analysisData.volatilityData
      default:
        return analysisData.priceData
    }
  }

  const getChartType = () => {
    switch (analysisType) {
      case 'volume':
        return 'bar'
      case 'volatility':
        return 'bar'
      default:
        return 'line'
    }
  }

  if (selectedAssets.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-400 opacity-50" />
          <h2 className="text-xl font-semibold text-white mb-2">
            {t('selectAssets')}
          </h2>
          <p className="text-gray-400">
            Choose assets from the sidebar to start analyzing
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {t('analysis')}
          </h1>
          <p className="text-gray-400">
            {t('performanceMetrics')} • {selectedAssets.length} assets selected
          </p>
        </div>
        
        <button className="flex items-center space-x-2 mt-4 sm:mt-0 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
          <Download className="h-4 w-4" />
          <span>{t('exportData')}</span>
        </button>
      </div>

      {/* Analysis Type Tabs */}
      <div className="flex flex-wrap gap-2">
        {analysisTypes.map((type) => (
          <button
            key={type.value}
            onClick={() => setAnalysisType(type.value)}
            className={`
              flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors
              ${analysisType === type.value
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }
            `}
          >
            <type.icon className="h-4 w-4" />
            <span>{type.label}</span>
          </button>
        ))}
      </div>

      {/* Timeframe Selector */}
      <div className="flex items-center space-x-2">
        <span className="text-gray-400 text-sm">Timeframe:</span>
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

      {/* Performance Metrics */}
      {analysisData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Average Return"
            value={`${analysisData.metrics.avgReturn}%`}
            change={analysisData.metrics.avgReturn}
            icon={TrendingUp}
            color="green"
          />
          <MetricCard
            title="Sharpe Ratio"
            value={analysisData.metrics.sharpeRatio.toFixed(2)}
            change={5.2}
            icon={BarChart3}
            color="blue"
          />
          <MetricCard
            title="Max Drawdown"
            value={`${analysisData.metrics.maxDrawdown}%`}
            change={analysisData.metrics.maxDrawdown}
            icon={Activity}
            color="red"
          />
          <MetricCard
            title="Correlation"
            value={analysisData.metrics.correlation.toFixed(2)}
            change={2.1}
            icon={TrendingUp}
            color="purple"
          />
        </div>
      )}

      {/* Main Chart */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {analysisTypes.find(t => t.value === analysisType)?.label}
          </h2>
          <div className="flex items-center space-x-2">
            <div className="flex space-x-2">
              {selectedAssets.map((asset, index) => (
                <div key={asset} className="flex items-center space-x-1">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: `hsl(${index * 60}, 70%, 50%)` }}
                  />
                  <span className="text-sm text-gray-300">{asset}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : (
          <Chart 
            data={getCurrentChartData()} 
            type={getChartType()}
            options={{
              plugins: {
                legend: {
                  display: selectedAssets.length > 1
                }
              }
            }}
          />
        )}
      </div>

      {/* Asset Performance Table */}
      {analysisData && (
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Asset Performance Summary
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 text-gray-400 font-medium">Asset</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Current Price</th>
                  <th className="text-right py-3 text-gray-400 font-medium">24h Change</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Volume</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Volatility</th>
                </tr>
              </thead>
              <tbody>
                {selectedAssets.map((asset, index) => (
                  <tr key={asset} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-4">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                          style={{ backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.2)`, color: `hsl(${index * 60}, 70%, 50%)` }}
                        >
                          {asset}
                        </div>
                        <span className="text-white font-medium">{asset}</span>
                      </div>
                    </td>
                    <td className="text-right py-4 text-white">
                      ${(1000 + Math.random() * 50000).toLocaleString()}
                    </td>
                    <td className="text-right py-4">
                      <span className={`${Math.random() > 0.5 ? 'text-green-400' : 'text-red-400'}`}>
                        {Math.random() > 0.5 ? '+' : '-'}{(Math.random() * 10).toFixed(2)}%
                      </span>
                    </td>
                    <td className="text-right py-4 text-gray-300">
                      ${(Math.random() * 1000000).toLocaleString()}
                    </td>
                    <td className="text-right py-4 text-gray-300">
                      {(10 + Math.random() * 30).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Analysis
