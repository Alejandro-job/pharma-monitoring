import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../config/theme.dart';
import '../../providers/data_provider.dart';
import '../../widgets/chart_card.dart';

class EnvironmentScreen extends StatelessWidget {
  const EnvironmentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: const Text('Monitoreo Ambiental'),
      ),
      body: Consumer<DataProvider>(
        builder: (context, provider, _) {
          final envData = provider.environmentData;
          final latestData = provider.latestEnvironmentData;
          final stats = provider.environmentStats;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCurrentConditions(latestData),
                const SizedBox(height: 24),
                _buildRoomStatus(),
                const SizedBox(height: 24),
                _buildTemperatureChart(envData),
                _buildHumidityChart(envData),
                _buildParticleChart(envData),
                const SizedBox(height: 24),
                _buildStatistics(stats),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentConditions(latestData) {
    if (latestData == null) {
      return const Center(child: CircularProgressIndicator());
    }
    
    final allInSpec = latestData.temperatureInSpec && 
                      latestData.humidityInSpec && 
                      latestData.pressureInSpec;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.secondary.withValues(alpha: 0.1),
            AppColors.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.secondary.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const FaIcon(FontAwesomeIcons.wind, color: AppColors.secondary, size: 20),
              const SizedBox(width: 12),
              const Text(
                'Condiciones Actuales',
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
                  'Sala: ${latestData.roomId}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              _buildConditionCard(
                'Temperatura',
                '${latestData.temperature.toStringAsFixed(1)}°C',
                FontAwesomeIcons.temperatureHalf,
                latestData.temperatureInSpec,
                '18-25°C',
              ),
              const SizedBox(width: 12),
              _buildConditionCard(
                'Humedad',
                '${latestData.humidity.toStringAsFixed(1)}%',
                FontAwesomeIcons.droplet,
                latestData.humidityInSpec,
                '30-65%',
              ),
              const SizedBox(width: 12),
              _buildConditionCard(
                'Presion Dif.',
                '${latestData.differentialPressure.toStringAsFixed(1)} Pa',
                FontAwesomeIcons.gaugeHigh,
                latestData.pressureInSpec,
                '>= 10 Pa',
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildConditionCard(
                'Particulas 0.5µm',
                '${latestData.particleCount05}',
                FontAwesomeIcons.virus,
                latestData.particleCount05 < 352000,
                '< 352,000/m³',
              ),
              const SizedBox(width: 12),
              _buildConditionCard(
                'Particulas 5.0µm',
                '${latestData.particleCount50}',
                FontAwesomeIcons.circle,
                latestData.particleCount50 < 2930,
                '< 2,930/m³',
              ),
              const SizedBox(width: 12),
              _buildConditionCard(
                'Clasificacion',
                latestData.cleanroomClass,
                FontAwesomeIcons.certificate,
                true,
                'ISO 7/8',
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: allInSpec 
                  ? AppColors.success.withValues(alpha: 0.1) 
                  : AppColors.warning.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FaIcon(
                  allInSpec ? FontAwesomeIcons.circleCheck : FontAwesomeIcons.triangleExclamation,
                  size: 14,
                  color: allInSpec ? AppColors.success : AppColors.warning,
                ),
                const SizedBox(width: 8),
                Text(
                  allInSpec ? 'Ambiente controlado - En especificacion' : 'Atencion: Revisar parametros',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: allInSpec ? AppColors.success : AppColors.warning,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildConditionCard(String label, String value, IconData icon, bool inSpec, String spec) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surfaceLight,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: inSpec ? AppColors.border : AppColors.warning.withValues(alpha: 0.5),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                FaIcon(icon, size: 12, color: AppColors.textMuted),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    label,
                    style: const TextStyle(fontSize: 10, color: AppColors.textMuted),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: inSpec ? AppColors.textPrimary : AppColors.warning,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              spec,
              style: const TextStyle(fontSize: 8, color: AppColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoomStatus() {
    final rooms = [
      {'id': 'PROD-A', 'name': 'Produccion A', 'class': 'ISO 7', 'status': true},
      {'id': 'PROD-B', 'name': 'Produccion B', 'class': 'ISO 7', 'status': true},
      {'id': 'PACK-1', 'name': 'Empaque', 'class': 'ISO 8', 'status': true},
      {'id': 'QC-LAB', 'name': 'Control de Calidad', 'class': 'ISO 7', 'status': false},
    ];
    
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
            'Estado de Salas',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          ...rooms.map((room) => _buildRoomRow(room)),
        ],
      ),
    ).animate().fadeIn(delay: 100.ms);
  }

  Widget _buildRoomRow(Map<String, dynamic> room) {
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
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: room['status'] ? AppColors.success : AppColors.warning,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: (room['status'] ? AppColors.success : AppColors.warning).withValues(alpha: 0.4),
                  blurRadius: 6,
                  spreadRadius: 1,
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  room['name'],
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                ),
                Text(
                  room['id'],
                  style: const TextStyle(fontSize: 10, color: AppColors.textMuted),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              room['class'],
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppColors.primary,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            room['status'] ? 'OK' : 'Alerta',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: room['status'] ? AppColors.success : AppColors.warning,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTemperatureChart(List envData) {
    final recentData = envData.length > 100 
        ? envData.sublist(envData.length - 100) 
        : envData;
    
    return ChartCard(
      title: 'Tendencia de Temperatura',
      subtitle: 'Ultimas 100 lecturas | Rango: 18-25°C',
      child: SizedBox(
        height: 180,
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
                  return FlSpot(entry.key.toDouble(), entry.value.temperature);
                }).toList(),
                isCurved: true,
                color: AppColors.error,
                barWidth: 2,
                dotData: const FlDotData(show: false),
                belowBarData: BarAreaData(
                  show: true,
                  color: AppColors.error.withValues(alpha: 0.1),
                ),
              ),
            ],
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(y: 18, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 25, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 21.5, color: AppColors.success, strokeWidth: 2),
              ],
            ),
            minY: 15,
            maxY: 28,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 200.ms);
  }

  Widget _buildHumidityChart(List envData) {
    final recentData = envData.length > 100 
        ? envData.sublist(envData.length - 100) 
        : envData;
    
    return ChartCard(
      title: 'Tendencia de Humedad Relativa',
      subtitle: 'Ultimas 100 lecturas | Rango: 30-65%',
      child: SizedBox(
        height: 180,
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
                  return FlSpot(entry.key.toDouble(), entry.value.humidity);
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
                HorizontalLine(y: 30, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 65, color: AppColors.warning, strokeWidth: 1, dashArray: [4, 4]),
                HorizontalLine(y: 47.5, color: AppColors.success, strokeWidth: 2),
              ],
            ),
            minY: 20,
            maxY: 75,
          ),
        ),
      ),
    ).animate().fadeIn(delay: 300.ms);
  }

  Widget _buildParticleChart(List envData) {
    final recentData = envData.length > 50 
        ? envData.sublist(envData.length - 50) 
        : envData;
    
    return ChartCard(
      title: 'Conteo de Particulas (0.5µm)',
      subtitle: 'Ultimas 50 lecturas | Limite ISO 7: 352,000/m³',
      child: SizedBox(
        height: 180,
        child: BarChart(
          BarChartData(
            barGroups: recentData.asMap().entries.map((entry) {
              final inSpec = entry.value.particleCount05 < 352000;
              return BarChartGroupData(
                x: entry.key,
                barRods: [
                  BarChartRodData(
                    toY: entry.value.particleCount05.toDouble() / 1000,
                    color: inSpec ? AppColors.secondary : AppColors.error,
                    width: 6,
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
                sideTitles: SideTitles(showTitles: true, reservedSize: 45),
              ),
            ),
            borderData: FlBorderData(show: false),
            extraLinesData: ExtraLinesData(
              horizontalLines: [
                HorizontalLine(y: 352, color: AppColors.error, strokeWidth: 2, dashArray: [8, 4]),
              ],
            ),
            maxY: 500,
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
            'Estadisticas Ambientales',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatItem('Temp. Promedio', '${stats['temperature_avg']?.toStringAsFixed(1) ?? 'N/A'}°C'),
              _buildStatItem('Humedad Promedio', '${stats['humidity_avg']?.toStringAsFixed(1) ?? 'N/A'}%'),
              _buildStatItem('Presion Promedio', '${stats['pressure_avg']?.toStringAsFixed(1) ?? 'N/A'} Pa'),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildStatItem(
                'Tasa de Anomalias',
                '${stats['anomaly_rate']?.toStringAsFixed(1) ?? '0'}%',
                isHighlighted: (stats['anomaly_rate'] ?? 0) > 2,
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
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: valueColor)),
        ],
      ),
    );
  }
}
