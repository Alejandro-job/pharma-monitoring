import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../config/theme.dart';
import '../../providers/data_provider.dart';
import '../../widgets/chart_card.dart';
import '../../models/sensor_data.dart';

class WaterScreen extends StatelessWidget {
  const WaterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: const Text('Sistema de Agua Purificada'),
      ),
      body: Consumer<DataProvider>(
        builder: (context, provider, _) {
          final waterData = provider.waterData;
          final latestData = provider.latestWaterData;
          final stats = provider.waterStats;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Current Values
                _buildCurrentValues(latestData),
                
                const SizedBox(height: 24),
                
                // Specifications Card
                _buildSpecifications(),
                
                const SizedBox(height: 24),
                
                // Charts
                _buildConductivityChart(waterData),
                _buildTOCChart(waterData),
                _buildPHChart(waterData),
                
                const SizedBox(height: 24),
                
                // Statistics
                _buildStatistics(stats),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentValues(WaterSystemData? data) {
    if (data == null) {
      return const Center(child: CircularProgressIndicator());
    }
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.info.withValues(alpha: 0.1),
            AppColors.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.info.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const FaIcon(FontAwesomeIcons.droplet, color: AppColors.info, size: 20),
              const SizedBox(width: 12),
              const Text(
                'Lecturas en Tiempo Real',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: data.allInSpec ? AppColors.success.withValues(alpha: 0.1) : AppColors.error.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  data.allInSpec ? 'EN ESPECIFICACION' : 'FUERA DE SPEC',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: data.allInSpec ? AppColors.success : AppColors.error,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              _buildValueCard(
                'Conductividad',
                '${data.conductivity.toStringAsFixed(2)} µS/cm',
                data.conductivityInSpec,
                '<= 1.3 µS/cm',
              ),
              const SizedBox(width: 12),
              _buildValueCard(
                'TOC',
                '${data.toc.toStringAsFixed(0)} ppb',
                data.tocInSpec,
                '<= 500 ppb',
              ),
              const SizedBox(width: 12),
              _buildValueCard(
                'pH',
                data.ph.toStringAsFixed(2),
                data.phInSpec,
                '5.0 - 7.0',
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildValueCard(
                'Temperatura',
                '${data.temperature.toStringAsFixed(1)} °C',
                true,
                '20-25 °C',
              ),
              const SizedBox(width: 12),
              _buildValueCard(
                'Flujo',
                '${data.flowRate.toStringAsFixed(1)} L/min',
                true,
                '> 40 L/min',
              ),
              const SizedBox(width: 12),
              const Spacer(),
            ],
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildValueCard(String label, String value, bool inSpec, String spec) {
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
              style: const TextStyle(
                fontSize: 11,
                color: AppColors.textMuted,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: inSpec ? AppColors.textPrimary : AppColors.error,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              spec,
              style: const TextStyle(
                fontSize: 9,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpecifications() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Especificaciones USP para Agua Purificada',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildSpecRow('Conductividad', '<= 1.3 µS/cm @ 25°C'),
          _buildSpecRow('TOC', '<= 500 ppb'),
          _buildSpecRow('pH', '5.0 - 7.0'),
          _buildSpecRow('Endotoxinas', '< 0.25 EU/mL'),
          _buildSpecRow('Conteo Microbiano', '< 100 CFU/mL'),
        ],
      ),
    ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildSpecRow(String parameter, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            parameter,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConductivityChart(List<WaterSystemData> data) {
    final recentData = data.length > 100 ? data.sublist(data.length - 100) : data;
    
    return ChartCard(
      title: 'Tendencia de Conductividad',
      subtitle: 'Últimas 100 lecturas | Límite USP: 1.3 µS/cm',
      child: SizedBox(
        height: 200,
        child: LineChart(
          LineChartData(
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              horizontalInterval: 0.3,
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
            lineBarsData: [
              LineChartBarData(
                spots: recentData.asMap().entries.map((entry) {
                  return FlSpot(entry.key.toDouble(), entry.value.conductivity);
                }).toList(),
                isCurved: true,
                color: AppColors.info,
                barWidth: 2,
                dotData: const FlDotData(show: false),
                belowBarData: BarAreaData(
                  show: true,
                  color: AppColors.info.withValues(alpha: 0.1),
                ),
              ),
            ],
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(
                  y: 1.3,
                  color: AppColors.error,
                  strokeWidth: 2,
                  dashArray: [8, 4],
                  label: HorizontalLineLabel(
                    show: true,
                    labelResolver: (line) => 'Límite USP',
                    style: const TextStyle(color: AppColors.error, fontSize: 10),
                  ),
                ),
              ],
            ),
            minY: 0,
            maxY: 2.0,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 200.ms);
  }

  Widget _buildTOCChart(List<WaterSystemData> data) {
    final recentData = data.length > 100 ? data.sublist(data.length - 100) : data;
    
    return ChartCard(
      title: 'Carbono Orgánico Total (TOC)',
      subtitle: 'Últimas 100 lecturas | Límite USP: 500 ppb',
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
                sideTitles: SideTitles(showTitles: true, reservedSize: 45),
              ),
            ),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: recentData.asMap().entries.map((entry) {
                  return FlSpot(entry.key.toDouble(), entry.value.toc);
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
                HorizontalLine(
                  y: 500,
                  color: AppColors.error,
                  strokeWidth: 2,
                  dashArray: [8, 4],
                ),
              ],
            ),
            minY: 0,
            maxY: 700,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 300.ms);
  }

  Widget _buildPHChart(List<WaterSystemData> data) {
    final recentData = data.length > 100 ? data.sublist(data.length - 100) : data;
    
    return ChartCard(
      title: 'pH del Agua',
      subtitle: 'Últimas 100 lecturas | Rango USP: 5.0 - 7.0',
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
                  return FlSpot(entry.key.toDouble(), entry.value.ph);
                }).toList(),
                isCurved: true,
                color: AppColors.success,
                barWidth: 2,
                dotData: const FlDotData(show: false),
                belowBarData: BarAreaData(
                  show: true,
                  color: AppColors.success.withValues(alpha: 0.1),
                ),
              ),
            ],
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(y: 5.0, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 7.0, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
              ],
            ),
            minY: 4,
            maxY: 8,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 400.ms);
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
            'Estadísticas (Últimas 100 lecturas)',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatItem(
                'Conductividad Prom.',
                '${stats['conductivity_avg']?.toStringAsFixed(3) ?? 'N/A'} µS/cm',
              ),
              _buildStatItem(
                'TOC Promedio',
                '${stats['toc_avg']?.toStringAsFixed(0) ?? 'N/A'} ppb',
              ),
              _buildStatItem(
                'pH Promedio',
                stats['ph_avg']?.toStringAsFixed(2) ?? 'N/A',
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildStatItem(
                'Tasa de Anomalías',
                '${stats['anomaly_rate']?.toStringAsFixed(1) ?? '0'}%',
                isHighlighted: (stats['anomaly_rate'] ?? 0) > 5,
              ),
              _buildStatItem(
                'Cumplimiento',
                '${stats['compliance_rate']?.toStringAsFixed(1) ?? '0'}%',
                isSuccess: (stats['compliance_rate'] ?? 0) >= 95,
              ),
              const Spacer(),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 500.ms);
  }

  Widget _buildStatItem(String label, String value, {bool isHighlighted = false, bool isSuccess = false}) {
    Color valueColor = AppColors.textPrimary;
    if (isHighlighted) valueColor = AppColors.error;
    if (isSuccess) valueColor = AppColors.success;
    
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }
}
