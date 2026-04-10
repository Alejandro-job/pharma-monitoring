import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../config/theme.dart';
import '../../providers/data_provider.dart';
import '../../providers/alerts_provider.dart';
import '../../widgets/stat_card.dart';
import '../../widgets/chart_card.dart';
import '../../widgets/status_indicator.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Start simulation when dashboard loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DataProvider>().startSimulation();
      context.read<AlertsProvider>().startMonitoring();
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDesktop = context.isDesktop;
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Panel de Control',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              'Sistema de Monitoreo Farmacéutico',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
        actions: [
          Consumer<DataProvider>(
            builder: (context, provider, _) {
              return IconButton(
                onPressed: () {
                  if (provider.isSimulating) {
                    provider.stopSimulation();
                  } else {
                    provider.startSimulation();
                  }
                },
                icon: FaIcon(
                  provider.isSimulating 
                      ? FontAwesomeIcons.pause 
                      : FontAwesomeIcons.play,
                  size: 16,
                ),
                tooltip: provider.isSimulating 
                    ? 'Pausar simulación' 
                    : 'Iniciar simulación',
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Cards Row
            _buildStatusCards(isDesktop),
            
            const SizedBox(height: 24),
            
            // System Status
            _buildSystemStatus(),
            
            const SizedBox(height: 24),
            
            // Charts
            _buildChartsSection(isDesktop),
            
            const SizedBox(height: 24),
            
            // Recent Alerts
            _buildRecentAlerts(),
            
            const SizedBox(height: 24),
            
            // ML Model Performance
            _buildMLPerformance(isDesktop),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCards(bool isDesktop) {
    return Consumer2<DataProvider, AlertsProvider>(
      builder: (context, dataProvider, alertsProvider, _) {
        final waterStats = dataProvider.waterStats;
        final tabletStats = dataProvider.tabletStats;
        final envStats = dataProvider.environmentStats;
        
        final cards = [
          StatCard(
            title: 'Agua - Cumplimiento',
            value: '${waterStats['compliance_rate']?.toStringAsFixed(1) ?? '0'}%',
            subtitle: 'Últimas 100 lecturas',
            icon: FontAwesomeIcons.droplet,
            iconColor: AppColors.info,
            trend: (waterStats['compliance_rate'] ?? 0) >= 95 
                ? TrendDirection.up 
                : TrendDirection.down,
          ),
          StatCard(
            title: 'Tabletas - Rendimiento',
            value: '${tabletStats['yield_rate']?.toStringAsFixed(1) ?? '0'}%',
            subtitle: 'Últimos 50 lotes',
            icon: FontAwesomeIcons.pills,
            iconColor: AppColors.success,
            trend: (tabletStats['yield_rate'] ?? 0) >= 95 
                ? TrendDirection.up 
                : TrendDirection.down,
          ),
          StatCard(
            title: 'Ambiente - Cumplimiento',
            value: '${envStats['compliance_rate']?.toStringAsFixed(1) ?? '0'}%',
            subtitle: 'Últimas 100 lecturas',
            icon: FontAwesomeIcons.wind,
            iconColor: AppColors.secondary,
            trend: (envStats['compliance_rate'] ?? 0) >= 95 
                ? TrendDirection.up 
                : TrendDirection.down,
          ),
          StatCard(
            title: 'Alertas Activas',
            value: alertsProvider.unacknowledgedCount.toString(),
            subtitle: '${alertsProvider.criticalCount} críticas',
            icon: FontAwesomeIcons.bell,
            iconColor: alertsProvider.criticalCount > 0 
                ? AppColors.error 
                : AppColors.warning,
            trend: alertsProvider.unacknowledgedCount > 5 
                ? TrendDirection.down 
                : TrendDirection.neutral,
          ),
        ];
        
        if (isDesktop) {
          return Row(
            children: cards.asMap().entries.map((entry) {
              return Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                    right: entry.key < cards.length - 1 ? 16 : 0,
                  ),
                  child: entry.value,
                ).animate()
                  .fadeIn(delay: Duration(milliseconds: entry.key * 100))
                  .slideX(begin: 0.1, end: 0),
              );
            }).toList(),
          );
        }
        
        return GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: cards.asMap().entries.map((entry) {
            return entry.value.animate()
              .fadeIn(delay: Duration(milliseconds: entry.key * 100))
              .slideY(begin: 0.1, end: 0);
          }).toList(),
        );
      },
    );
  }

  Widget _buildSystemStatus() {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Estado del Sistema',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  StatusIndicator(
                    isActive: provider.isSimulating,
                    label: provider.isSimulating 
                        ? 'En Tiempo Real' 
                        : 'Pausado',
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  _buildSystemModule(
                    'Sistema de Agua',
                    FontAwesomeIcons.droplet,
                    AppColors.info,
                    provider.latestWaterData?.allInSpec ?? true,
                  ),
                  const SizedBox(width: 24),
                  _buildSystemModule(
                    'Producción',
                    FontAwesomeIcons.industry,
                    AppColors.success,
                    true,
                  ),
                  const SizedBox(width: 24),
                  _buildSystemModule(
                    'Ambiente',
                    FontAwesomeIcons.wind,
                    AppColors.secondary,
                    provider.latestEnvironmentData?.temperatureInSpec ?? true,
                  ),
                  const SizedBox(width: 24),
                  _buildSystemModule(
                    'ML Engine',
                    FontAwesomeIcons.brain,
                    AppColors.primary,
                    true,
                  ),
                ],
              ),
            ],
          ),
        ).animate().fadeIn().slideY(begin: 0.1, end: 0);
      },
    );
  }

  Widget _buildSystemModule(
    String name, 
    IconData icon, 
    Color color,
    bool isOk,
  ) {
    return Expanded(
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 16),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: isOk ? AppColors.success : AppColors.warning,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      isOk ? 'Normal' : 'Alerta',
                      style: TextStyle(
                        fontSize: 10,
                        color: isOk ? AppColors.success : AppColors.warning,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartsSection(bool isDesktop) {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        final waterData = provider.waterData;
        final recentWater = waterData.length > 50 
            ? waterData.sublist(waterData.length - 50) 
            : waterData;
        
        final charts = [
          ChartCard(
            title: 'Conductividad del Agua',
            subtitle: 'Últimos 50 puntos | Límite: 1.3 µS/cm',
            child: _buildLineChart(
              recentWater.map((d) => d.conductivity).toList(),
              AppColors.info,
              1.3,
            ),
          ),
          ChartCard(
            title: 'TOC (Carbono Orgánico Total)',
            subtitle: 'Últimos 50 puntos | Límite: 500 ppb',
            child: _buildLineChart(
              recentWater.map((d) => d.toc).toList(),
              AppColors.secondary,
              500,
            ),
          ),
        ];
        
        if (isDesktop) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: charts.map((chart) {
              return Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                    right: charts.indexOf(chart) == 0 ? 16 : 0,
                  ),
                  child: chart,
                ),
              );
            }).toList(),
          );
        }
        
        return Column(children: charts);
      },
    );
  }

  Widget _buildLineChart(List<double> data, Color color, double limit) {
    if (data.isEmpty) {
      return const Center(child: Text('Sin datos'));
    }
    
    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: limit / 4,
            getDrawingHorizontalLine: (value) => FlLine(
              color: AppColors.border,
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            show: true,
            rightTitles: const AxisTitles(),
            topTitles: const AxisTitles(),
            bottomTitles: const AxisTitles(),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toStringAsFixed(1),
                    style: const TextStyle(
                      color: AppColors.textMuted,
                      fontSize: 10,
                    ),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: data.asMap().entries.map((entry) {
                return FlSpot(entry.key.toDouble(), entry.value);
              }).toList(),
              isCurved: true,
              color: color,
              barWidth: 2,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: color.withValues(alpha: 0.1),
              ),
            ),
          ],
          extraLinesData: ExtraLinesData(
            horizontalLines: [
              HorizontalLine(
                y: limit,
                color: AppColors.error.withValues(alpha: 0.5),
                strokeWidth: 2,
                dashArray: [8, 4],
              ),
            ],
          ),
          minY: 0,
          maxY: limit * 1.5,
        ),
      ),
    );
  }

  Widget _buildRecentAlerts() {
    return Consumer<AlertsProvider>(
      builder: (context, provider, _) {
        final recentAlerts = provider.alerts.take(5).toList();
        
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Alertas Recientes',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  TextButton(
                    onPressed: () {},
                    child: const Text('Ver Todas'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (recentAlerts.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text(
                      'No hay alertas recientes',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  ),
                )
              else
                ...recentAlerts.map((alert) => _buildAlertItem(alert)),
            ],
          ),
        ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1, end: 0);
      },
    );
  }

  Widget _buildAlertItem(alert) {
    Color severityColor;
    switch (alert.severity) {
      case AlertSeverity.critical:
        severityColor = AppColors.error;
        break;
      case AlertSeverity.major:
        severityColor = AppColors.warning;
        break;
      case AlertSeverity.minor:
        severityColor = AppColors.info;
        break;
      default:
        severityColor = AppColors.textMuted;
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(8),
        border: Border(
          left: BorderSide(color: severityColor, width: 3),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.message,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${alert.source} | ${_formatTime(alert.timestamp)}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: severityColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              alert.severity.name.toUpperCase(),
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: severityColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMLPerformance(bool isDesktop) {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        final metrics = provider.modelMetrics;
        
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const FaIcon(
                    FontAwesomeIcons.brain,
                    size: 16,
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Rendimiento de Modelos ML',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              GridView.count(
                crossAxisCount: isDesktop ? 4 : 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: isDesktop ? 1.8 : 1.4,
                children: metrics.map((metric) {
                  return _buildModelCard(metric);
                }).toList(),
              ),
            ],
          ),
        ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.1, end: 0);
      },
    );
  }

  Widget _buildModelCard(metric) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            metric.modelName,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildMetricValue('F1', metric.f1Score),
              _buildMetricValue('AUC', metric.aucRoc),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: metric.accuracy,
            backgroundColor: AppColors.border,
            valueColor: AlwaysStoppedAnimation<Color>(
              metric.accuracy >= 0.95 ? AppColors.success : AppColors.warning,
            ),
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 4),
          Text(
            'Accuracy: ${(metric.accuracy * 100).toStringAsFixed(1)}%',
            style: const TextStyle(
              fontSize: 10,
              color: AppColors.textMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricValue(String label, double value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            color: AppColors.textMuted,
          ),
        ),
        Text(
          (value * 100).toStringAsFixed(1),
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
        ),
      ],
    );
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final diff = now.difference(dateTime);
    
    if (diff.inMinutes < 1) return 'Ahora';
    if (diff.inMinutes < 60) return 'Hace ${diff.inMinutes}m';
    if (diff.inHours < 24) return 'Hace ${diff.inHours}h';
    return 'Hace ${diff.inDays}d';
  }
}
