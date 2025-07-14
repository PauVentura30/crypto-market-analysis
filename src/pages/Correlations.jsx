import { useState, useEffect } from 'react'
import { GitBranch, Download, RefreshCw, Info } from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'

const Correlations = ({ selectedAssets }) => {
  const { t } = useLanguage()
  const [correlationMatrix, setCorrelationMatrix] = useState(null)
  const [timeframe, setTimeframe] = useState('30D')
  const [loading, setLoading] = useState(false)
  const [hoveredCell, setHoveredCell] = useState(null)

  useEffect(() => {
    if (selectedAssets.length >= 2) {
      setLoading(true)
      
      // Simulate API call for correlation calculation
      setTimeout(() => {
        const matrix = generateCorrelationMatrix(selectedAssets)
        setCorrelationMatrix(matrix)
        setLoading(false)
      }, 1000)
    }
  }, [selectedAssets, timeframe])

  const generateCorrelationMatrix = (assets) => {
    const matrix = {}
    assets.forEach(asset1 => {
      matrix[asset1] = {}
      assets.forEach(asset2 => {
        if (asset1 === asset2) {
          matrix[asset1][asset2] = 1.0
        } else {
          // Generate realistic correlation values
          matrix[asset1][asset2] = (Math.random() * 2 - 1).toFixed(3)
        }
      })
    })
    return matrix
  }

  const getCorrelationColor = (value) => {
    const absValue = Math.abs(value)
    if (absValue >= 0.8) return 'bg-red-500'
    if (absValue >= 0.6) return 'bg-orange-500'
    if (absValue >= 0.4) return 'bg-yellow-500'
    if (absValue >= 0.2) return 'bg-green-500'
    return 'bg-blue-500'
  }

  const getCorrelationDescription = (value) => {
    const absValue = Math.abs(value)
    if (absValue >= 0.8) return 'Very Strong'
    if (absValue >= 0.6) return 'Strong'
    if (absValue >= 0.4) return 'Moderate'
    if (absValue >= 0.2) return 'Weak'
    return 'Very Weak'
  }

  const timeframes = [
    { value: '7D', label: t('week') },
    { value: '30D', label: t('month') },
    { value: '3M', label: t('quarter') },
    { value: '1Y', label: t('year') }
  ]

  if (selectedAssets.length < 2) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <GitBranch className="h-16 w-16 mx-auto mb-4 text-gray-400 opacity-50" />
          <h2 className="text-xl font-semibold text-white mb-2">
            Select at least 2 assets
          </h2>
          <p className="text-gray-400">
            Choose multiple assets from the sidebar to analyze correlations
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
            {t('correlations')}
          </h1>
          <p className="text-gray-400">
            {t('correlationMatrix')} • {selectedAssets.length} assets selected
          </p>
        </div>
        
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          <button
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            <Download className="h-4 w-4" />
            <span>{t('exportData')}</span>
          </button>
        </div>
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

      {/* Info Panel */}
      <div className="backdrop-blur-xl bg-blue-500/10 border border-blue-500/20 rounded-2xl p-4">
        <div className="flex items-start space-x-3">
          <Info className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-blue-400 font-medium mb-1">Correlation Interpretation</h3>
            <p className="text-sm text-gray-300">
              Correlation values range from -1 to 1. Values near 1 indicate strong positive correlation, 
              near -1 indicate strong negative correlation, and near 0 indicate little to no correlation.
            </p>
          </div>
        </div>
      </div>

      {/* Correlation Matrix */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            Correlation Matrix
          </h2>
          {hoveredCell && (
            <div className="text-sm text-gray-300">
              {hoveredCell.asset1} vs {hoveredCell.asset2}: {hoveredCell.value} 
              ({getCorrelationDescription(hoveredCell.value)})
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : correlationMatrix ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="p-3"></th>
                  {selectedAssets.map(asset => (
                    <th key={asset} className="p-3 text-center text-gray-400 font-medium min-w-20">
                      {asset}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {selectedAssets.map(asset1 => (
                  <tr key={asset1}>
                    <td className="p-3 text-gray-400 font-medium">
                      {asset1}
                    </td>
                    {selectedAssets.map(asset2 => {
                      const value = parseFloat(correlationMatrix[asset1][asset2])
                      return (
                        <td 
                          key={asset2} 
                          className="p-1"
                          onMouseEnter={() => setHoveredCell({ asset1, asset2, value })}
                          onMouseLeave={() => setHoveredCell(null)}
                        >
                          <div 
                            className={`
                              w-16 h-16 flex items-center justify-center rounded-lg text-white text-sm font-bold
                              transition-all duration-200 hover:scale-110 cursor-pointer
                              ${getCorrelationColor(value)}
                            `}
                            style={{ opacity: Math.abs(value) * 0.8 + 0.2 }}
                          >
                            {value.toFixed(2)}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>

      {/* Correlation Legend */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Correlation Strength</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { range: '0.8 - 1.0', label: 'Very Strong', color: 'bg-red-500' },
            { range: '0.6 - 0.8', label: 'Strong', color: 'bg-orange-500' },
            { range: '0.4 - 0.6', label: 'Moderate', color: 'bg-yellow-500' },
            { range: '0.2 - 0.4', label: 'Weak', color: 'bg-green-500' },
            { range: '0.0 - 0.2', label: 'Very Weak', color: 'bg-blue-500' }
          ].map(item => (
            <div key={item.range} className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded ${item.color}`}></div>
              <div>
                <div className="text-white text-sm font-medium">{item.label}</div>
                <div className="text-gray-400 text-xs">{item.range}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Correlation Insights */}
      {correlationMatrix && (
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Key Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-green-400 font-medium mb-2">Highest Positive Correlations</h4>
              <div className="space-y-2">
                {Object.entries(correlationMatrix)
                  .flatMap(([asset1, correlations]) => 
                    Object.entries(correlations)
                      .filter(([asset2, value]) => asset1 !== asset2 && value > 0)
                      .map(([asset2, value]) => ({ asset1, asset2, value: parseFloat(value) }))
                  )
                  .sort((a, b) => b.value - a.value)
                  .slice(0, 3)
                  .map(({ asset1, asset2, value }) => (
                    <div key={`${asset1}-${asset2}`} className="flex justify-between text-sm">
                      <span className="text-gray-300">{asset1} - {asset2}</span>
                      <span className="text-green-400 font-medium">+{value.toFixed(3)}</span>
                    </div>
                  ))
                }
              </div>
            </div>
            <div>
              <h4 className="text-red-400 font-medium mb-2">Highest Negative Correlations</h4>
              <div className="space-y-2">
                {Object.entries(correlationMatrix)
                  .flatMap(([asset1, correlations]) => 
                    Object.entries(correlations)
                      .filter(([asset2, value]) => asset1 !== asset2 && value < 0)
                      .map(([asset2, value]) => ({ asset1, asset2, value: parseFloat(value) }))
                  )
                  .sort((a, b) => a.value - b.value)
                  .slice(0, 3)
                  .map(({ asset1, asset2, value }) => (
                    <div key={`${asset1}-${asset2}`} className="flex justify-between text-sm">
                      <span className="text-gray-300">{asset1} - {asset2}</span>
                      <span className="text-red-400 font-medium">{value.toFixed(3)}</span>
                    </div>
                  ))
                }
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Correlations
