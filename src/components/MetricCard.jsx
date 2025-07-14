import { TrendingUp, TrendingDown } from 'lucide-react'

const MetricCard = ({ title, value, change, icon: Icon, color = 'blue' }) => {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    green: 'from-green-500/20 to-green-600/20 border-green-500/30',
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
    orange: 'from-orange-500/20 to-orange-600/20 border-orange-500/30',
    red: 'from-red-500/20 to-red-600/20 border-red-500/30'
  }

  const iconColors = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
    orange: 'text-orange-400',
    red: 'text-red-400'
  }

  return (
    <div className={`
      backdrop-blur-xl bg-gradient-to-br ${colorClasses[color]} 
      border rounded-2xl p-6 hover:bg-white/10 transition-all duration-300
      hover:shadow-lg hover:shadow-${color}-500/10
    `}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl bg-${color}-500/20`}>
          <Icon className={`h-6 w-6 ${iconColors[color]}`} />
        </div>
        <div className="text-right">
          {change !== undefined && (
            <div className={`
              flex items-center space-x-1 text-sm
              ${change >= 0 ? 'text-green-400' : 'text-red-400'}
            `}>
              {change >= 0 ? (
                <TrendingUp className="h-4 w-4" />
              ) : (
                <TrendingDown className="h-4 w-4" />
              )}
              <span>{change >= 0 ? '+' : ''}{change}%</span>
            </div>
          )}
        </div>
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-white mb-1">
          {value}
        </h3>
        <p className="text-gray-400 text-sm">
          {title}
        </p>
      </div>
    </div>
  )
}

export default MetricCard
