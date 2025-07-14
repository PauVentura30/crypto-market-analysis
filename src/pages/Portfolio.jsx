import { useState, useEffect } from 'react'
import { PieChart, Plus, Trash2, Edit3, Download, Target } from 'lucide-react'
import { useLanguage } from '../utils/LanguageContext'
import Chart from '../components/Chart'
import MetricCard from '../components/MetricCard'

const Portfolio = ({ selectedAssets }) => {
  const { t } = useLanguage()
  const [portfolio, setPortfolio] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingPosition, setEditingPosition] = useState(null)
  const [newPosition, setNewPosition] = useState({ asset: '', quantity: '', price: '' })

  useEffect(() => {
    // Initialize with some sample portfolio data
    if (selectedAssets.length > 0 && portfolio.length === 0) {
      const samplePortfolio = selectedAssets.slice(0, 3).map((asset, index) => ({
        id: Date.now() + index,
        asset: asset,
        quantity: 100 + Math.random() * 1000,
        avgPrice: 1000 + Math.random() * 50000,
        currentPrice: 1000 + Math.random() * 50000,
        allocation: 25 + Math.random() * 25
      }))
      setPortfolio(samplePortfolio)
    }
  }, [selectedAssets, portfolio.length])

  const portfolioValue = portfolio.reduce((total, position) => {
    return total + (position.quantity * position.currentPrice)
  }, 0)

  const totalPnL = portfolio.reduce((total, position) => {
    return total + (position.quantity * (position.currentPrice - position.avgPrice))
  }, 0)

  const totalPnLPercent = portfolioValue > 0 ? (totalPnL / (portfolioValue - totalPnL)) * 100 : 0

  const pieChartData = {
    labels: portfolio.map(p => p.asset),
    datasets: [{
      data: portfolio.map(p => p.quantity * p.currentPrice),
      backgroundColor: portfolio.map((_, index) => `hsl(${index * 60}, 70%, 50%)`),
      borderColor: portfolio.map((_, index) => `hsl(${index * 60}, 70%, 40%)`),
      borderWidth: 2
    }]
  }

  const addPosition = () => {
    if (newPosition.asset && newPosition.quantity && newPosition.price) {
      const position = {
        id: Date.now(),
        asset: newPosition.asset,
        quantity: parseFloat(newPosition.quantity),
        avgPrice: parseFloat(newPosition.price),
        currentPrice: parseFloat(newPosition.price) * (1 + (Math.random() - 0.5) * 0.1),
        allocation: 0
      }
      setPortfolio([...portfolio, position])
      setNewPosition({ asset: '', quantity: '', price: '' })
      setShowAddModal(false)
    }
  }

  const removePosition = (id) => {
    setPortfolio(portfolio.filter(p => p.id !== id))
  }

  const updatePosition = (id, updates) => {
    setPortfolio(portfolio.map(p => 
      p.id === id ? { ...p, ...updates } : p
    ))
    setEditingPosition(null)
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {t('portfolio')}
          </h1>
          <p className="text-gray-400">
            Portfolio Management • {portfolio.length} positions
          </p>
        </div>
        
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Add Position</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            <Download className="h-4 w-4" />
            <span>{t('exportData')}</span>
          </button>
        </div>
      </div>

      {/* Portfolio Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Value"
          value={`$${portfolioValue.toLocaleString()}`}
          change={totalPnLPercent}
          icon={Target}
          color="blue"
        />
        <MetricCard
          title="Total P&L"
          value={`$${totalPnL.toLocaleString()}`}
          change={totalPnLPercent}
          icon={PieChart}
          color={totalPnL >= 0 ? 'green' : 'red'}
        />
        <MetricCard
          title="Best Performer"
          value={portfolio.length > 0 ? portfolio[0].asset : '-'}
          change={portfolio.length > 0 ? ((portfolio[0].currentPrice - portfolio[0].avgPrice) / portfolio[0].avgPrice) * 100 : 0}
          icon={Target}
          color="green"
        />
        <MetricCard
          title="Positions"
          value={portfolio.length}
          change={5.2}
          icon={PieChart}
          color="purple"
        />
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocation Chart */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Portfolio Allocation
          </h2>
          {portfolio.length > 0 ? (
            <Chart data={pieChartData} type="doughnut" />
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <PieChart className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No positions in portfolio</p>
              </div>
            </div>
          )}
        </div>

        {/* Performance Summary */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Performance Summary
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Invested</span>
              <span className="text-white font-medium">
                ${(portfolioValue - totalPnL).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Current Value</span>
              <span className="text-white font-medium">
                ${portfolioValue.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Unrealized P&L</span>
              <span className={`font-medium ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${totalPnL.toLocaleString()} ({totalPnLPercent.toFixed(2)}%)
              </span>
            </div>
            <div className="border-t border-white/10 pt-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Best Position</span>
                <span className="text-green-400 font-medium">
                  {portfolio.length > 0 ? portfolio[0].asset : '-'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
        <h2 className="text-xl font-semibold text-white mb-6">
          Portfolio Positions
        </h2>
        
        {portfolio.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 text-gray-400 font-medium">Asset</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Quantity</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Avg Price</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Current Price</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Value</th>
                  <th className="text-right py-3 text-gray-400 font-medium">P&L</th>
                  <th className="text-right py-3 text-gray-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.map((position) => {
                  const value = position.quantity * position.currentPrice
                  const pnl = position.quantity * (position.currentPrice - position.avgPrice)
                  const pnlPercent = ((position.currentPrice - position.avgPrice) / position.avgPrice) * 100

                  return (
                    <tr key={position.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-4">
                        <span className="text-white font-medium">{position.asset}</span>
                      </td>
                      <td className="text-right py-4 text-white">
                        {position.quantity.toLocaleString()}
                      </td>
                      <td className="text-right py-4 text-gray-300">
                        ${position.avgPrice.toLocaleString()}
                      </td>
                      <td className="text-right py-4 text-white">
                        ${position.currentPrice.toLocaleString()}
                      </td>
                      <td className="text-right py-4 text-white font-medium">
                        ${value.toLocaleString()}
                      </td>
                      <td className="text-right py-4">
                        <div className={pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                          ${pnl.toLocaleString()}
                          <div className="text-xs">
                            ({pnlPercent.toFixed(2)}%)
                          </div>
                        </div>
                      </td>
                      <td className="text-right py-4">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => setEditingPosition(position.id)}
                            className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
                          >
                            <Edit3 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => removePosition(position.id)}
                            className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="h-32 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No positions in your portfolio</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="mt-2 text-blue-400 hover:text-blue-300 transition-colors"
              >
                Add your first position
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add Position Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-white mb-4">Add New Position</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Asset
                </label>
                <select
                  value={newPosition.asset}
                  onChange={(e) => setNewPosition({ ...newPosition, asset: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select an asset</option>
                  {selectedAssets.map(asset => (
                    <option key={asset} value={asset} className="bg-gray-800">
                      {asset}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Quantity
                </label>
                <input
                  type="number"
                  value={newPosition.quantity}
                  onChange={(e) => setNewPosition({ ...newPosition, quantity: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Average Price ($)
                </label>
                <input
                  type="number"
                  value={newPosition.price}
                  onChange={(e) => setNewPosition({ ...newPosition, price: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white"
              >
                Cancel
              </button>
              <button
                onClick={addPosition}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-white"
              >
                Add Position
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Portfolio
