import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../config/theme.dart';
import '../../providers/data_provider.dart';
import '../../widgets/chart_card.dart';

class TabletsScreen extends StatelessWidget {
  const TabletsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: const Text('Produccion de Tabletas'),
      ),
      body: Consumer<DataProvider>(
        builder: (context, provider, _) {
          final tabletData = provider.tabletData;
          final latestData = provider.latestTabletData;
          final stats = provider.tabletStats;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Current Batch
                _buildCurrentBatch(latestData),
                
                const SizedBox(height: 24),
                
                // Weight Distribution
                _buildWeightChart(tabletData),
                
                // Hardness Trend
                _buildHardnessChart(tabletData),
                
                const SizedBox(height: 24),
                
                // Statistics
                _buildStatistics(stats),
                
                const SizedBox(height: 24),
                
                // Recent Batches
                _buildRecentBatches(tabletData),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentBatch(latestData) {
    if (latestData == null) {
      return const Center(child: CircularProgressIndicator());
    }
    
    final allInSpec = latestData.weightInSpec && 
                      latestData.hardnessInSpec && 
                      latestData.friabilityInSpec;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.success.withValues(alpha: 0.1),
            AppColors.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.success.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const FaIcon(FontAwesomeIcons.pills, color: AppColors.success, size: 20),
              const SizedBox(width: 12),
              const Text(
                'Lote Actual',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.surfaceLight,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  latestData.batchId,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              _buildMetricCard('Peso', '${latestData.weight.toStringAsFixed(1)} mg', 
                  latestData.weightInSpec, '475-525 mg'),
              const SizedBox(width: 12),
              _buildMetricCard('Dureza', '${latestData.hardness.toStringAsFixed(1)} N', 
                  latestData.hardnessInSpec, '40-80 N'),
              const SizedBox(width: 12),
              _buildMetricCard('Friabilidad', '${latestData.friability.toStringAsFixed(2)}%', 
                  latestData.friabilityInSpec, '<= 1.0%'),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildMetricCard('Espesor', '${latestData.thickness.toStringAsFixed(2)} mm', 
                  true, '4.5-5.5 mm'),
              const SizedBox(width: 12),
              _buildMetricCard('Disolucion', '${latestData.dissolutionTime.toStringAsFixed(1)} min', 
                  true, '< 30 min'),
              const SizedBox(width: 12),
              _buildMetricCard('Uniformidad', '${latestData.contentUniformity.toStringAsFixed(1)}%', 
                  true, '85-115%'),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: allInSpec 
                  ? AppColors.success.withValues(alpha: 0.1) 
                  : AppColors.error.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FaIcon(
                  allInSpec ? FontAwesomeIcons.circleCheck : FontAwesomeIcons.triangleExclamation,
                  size: 14,
                  color: allInSpec ? AppColors.success : AppColors.error,
                ),
                const SizedBox(width: 8),
                Text(
                  allInSpec ? 'Lote dentro de especificaciones' : 'Alerta: Parametros fuera de rango',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: allInSpec ? AppColors.success : AppColors.error,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildMetricCard(String label, String value, bool inSpec, String spec) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surfaceLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: inSpec ? AppColors.border : AppColors.error.withValues(alpha: 0.5),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: inSpec ? AppColors.textPrimary : AppColors.error,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              spec,
              style: const TextStyle(fontSize: 9, color: AppColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeightChart(List tabletData) {
    final recentData = tabletData.length > 50 
        ? tabletData.sublist(tabletData.length - 50) 
        : tabletData;
    
    return ChartCard(
      title: 'Distribucion de Peso',
      subtitle: 'Ultimos 50 lotes | Target: 500 mg +/- 5%',
      child: SizedBox(
        height: 200,
        child: BarChart(
          BarChartData(
            barGroups: recentData.asMap().entries.map((entry) {
              final inSpec = entry.value.weightInSpec;
              return BarChartGroupData(
                x: entry.key,
                barRods: [
                  BarChartRodData(
                    toY: entry.value.weight,
                    color: inSpec ? AppColors.success : AppColors.error,
                    width: 4,
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(2)),
                  ),
                ],
              );
            }).toList(),
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              getDrawingHorizontalLine: (value) => FlLine(
                color: AppColors.border,
                strokeWidth: 1,
              ),
            ),
            titlesData: const FlTitlesData(
              show: true,
              rightTitles: AxisTitles(),
              topTitles: AxisTitles(),
              bottomTitles: AxisTitles(),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: true, reservedSize: 40),
              ),
            ),
            borderData: FlBorderData(show: false),
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(y: 500, color: AppColors.primary, strokeWidth: 2),
                HorizontalLine(y: 475, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 525, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
              ],
            ),
            minY: 450,
            maxY: 550,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 100.ms);
  }

  Widget _buildHardnessChart(List tabletData) {
    final recentData = tabletData.length > 50 
        ? tabletData.sublist(tabletData.length - 50) 
        : tabletData;
    
    return ChartCard(
      title: 'Tendencia de Dureza',
      subtitle: 'Ultimos 50 lotes | Rango: 40-80 N',
      child: SizedBox(
        height: 200,
        child: LineChart(
          LineChartData(
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              getDrawingHorizontalLine: (value) => FlLine(
                color: AppColors.border,
                strokeWidth: 1,
              ),
            ),
            titlesData: const FlTitlesData(
              show: true,
              rightTitles: AxisTitles(),
              topTitles: AxisTitles(),
              bottomTitles: AxisTitles(),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: true, reservedSize: 35),
              ),
            ),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: recentData.asMap().entries.map((entry) {
                  return FlSpot(entry.key.toDouble(), entry.value.hardness);
                }).toList(),
                isCurved: true,
                color: AppColors.secondary,
                barWidth: 2,
                dotData: const FlDotData(show: false),
                belowBarData: BarAreaData(
                  show: true,
                  color: AppColors.secondary.withValues(alpha: 0.1),
                ),
              ),
            ],
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(y: 40, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 80, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 60, color: AppColors.primary, strokeWidth: 2),
              ],
            ),
            minY: 30,
            maxY: 90,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 200.ms);
  }

  Widget _buildStatistics(Map<String, double> stats) {
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
          const Text(
            'Resumen de Produccion',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatItem('Peso Promedio', '${stats['weight_avg']?.toStringAsFixed(1) ?? 'N/A'} mg'),
              _buildStatItem('Dureza Promedio', '${stats['hardness_avg']?.toStringAsFixed(1) ?? 'N/A'} N'),
              _buildStatItem('Friabilidad Promedio', '${stats['friability_avg']?.toStringAsFixed(2) ?? 'N/A'}%'),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildStatItem(
                'Tasa de Anomalias',
                '${stats['anomaly_rate']?.toStringAsFixed(1) ?? '0'}%',
                isHighlighted: (stats['anomaly_rate'] ?? 0) > 3,
              ),
              _buildStatItem(
                'Rendimiento',
                '${stats['yield_rate']?.toStringAsFixed(1) ?? '0'}%',
                isSuccess: (stats['yield_rate'] ?? 0) >= 95,
              ),
              const Spacer(),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms);
  }

  Widget _buildStatItem(String label, String value, {bool isHighlighted = false, bool isSuccess = false}) {
    Color valueColor = AppColors.textPrimary;
    if (isHighlighted) valueColor = AppColors.error;
    if (isSuccess) valueColor = AppColors.success;
    
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: valueColor)),
        ],
      ),
    );
  }

  Widget _buildRecentBatches(List tabletData) {
    final recentBatches = tabletData.length > 10 
        ? tabletData.sublist(tabletData.length - 10).reversed.toList()
        : tabletData.reversed.toList();
    
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
          const Text(
            'Ultimos Lotes',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          ...recentBatches.take(5).map((batch) => _buildBatchRow(batch)),
        ],
      ),
    ).animate().fadeIn(delay: 400.ms);
  }

  Widget _buildBatchRow(batch) {
    final allInSpec = batch.weightInSpec && batch.hardnessInSpec && batch.friabilityInSpec;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: allInSpec ? AppColors.success : AppColors.error,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              batch.batchId,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                fontFamily: 'monospace',
              ),
            ),
          ),
          Text(
            '${batch.weight.toStringAsFixed(1)} mg',
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
          ),
          const SizedBox(width: 16),
          Text(
            '${batch.hardness.toStringAsFixed(1)} N',
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}
