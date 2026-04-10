import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../providers/data_provider.dart';
import '../../config/theme.dart';
import '../../widgets/chart_card.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) => [
          SliverAppBar(
            expandedHeight: 120,
            floating: true,
            pinned: true,
            backgroundColor: AppColors.surface,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                'Analítica Avanzada',
                style: AppTextStyles.h3.copyWith(color: AppColors.textPrimary),
              ),
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppColors.primary.withOpacity(0.2),
                      AppColors.surface,
                    ],
                  ),
                ),
              ),
            ),
            bottom: TabBar(
              controller: _tabController,
              indicatorColor: AppColors.primary,
              labelColor: AppColors.primary,
              unselectedLabelColor: AppColors.textSecondary,
              tabs: const [
                Tab(text: 'Resumen', icon: Icon(Icons.dashboard_outlined)),
                Tab(text: 'ML', icon: Icon(Icons.psychology_outlined)),
                Tab(text: 'Tendencias', icon: Icon(Icons.trending_up)),
                Tab(text: 'Correlación', icon: Icon(Icons.scatter_plot)),
              ],
            ),
          ),
        ],
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildSummaryTab(),
            _buildMLTab(),
            _buildTrendsTab(),
            _buildCorrelationTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryTab() {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        final stats = provider.getStatistics();
        
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSectionTitle('Estadísticas Globales'),
            const SizedBox(height: 16),
            _buildStatsGrid(stats),
            const SizedBox(height: 24),
            _buildSectionTitle('Distribución de Datos'),
            const SizedBox(height: 16),
            _buildDistributionChart(provider),
            const SizedBox(height: 24),
            _buildSectionTitle('Comparativa por Sistema'),
            const SizedBox(height: 16),
            _buildSystemComparison(provider),
          ],
        );
      },
    );
  }

  Widget _buildMLTab() {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSectionTitle('Modelos de Machine Learning'),
            const SizedBox(height: 16),
            _buildMLModelCard(
              'Isolation Forest',
              'Detección de anomalías basada en aislamiento',
              0.94,
              0.92,
              Icons.forest,
              AppColors.success,
            ),
            const SizedBox(height: 12),
            _buildMLModelCard(
              'Local Outlier Factor',
              'Detección basada en densidad local',
              0.91,
              0.89,
              Icons.blur_circular,
              AppColors.info,
            ),
            const SizedBox(height: 12),
            _buildMLModelCard(
              'One-Class SVM',
              'Clasificación de una clase',
              0.88,
              0.86,
              Icons.category,
              AppColors.warning,
            ),
            const SizedBox(height: 12),
            _buildMLModelCard(
              'Autoencoder',
              'Red neuronal para reconstrucción',
              0.96,
              0.94,
              Icons.memory,
              AppColors.primary,
            ),
            const SizedBox(height: 24),
            _buildSectionTitle('Curva ROC'),
            const SizedBox(height: 16),
            _buildROCCurve(),
            const SizedBox(height: 24),
            _buildSectionTitle('Matriz de Confusión'),
            const SizedBox(height: 16),
            _buildConfusionMatrix(),
          ],
        );
      },
    );
  }

  Widget _buildTrendsTab() {
    return Consumer<DataProvider>(
      builder: (context, provider, _) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSectionTitle('Tendencias Temporales'),
            const SizedBox(height: 16),
            ChartCard(
              title: 'Conductividad del Agua (24h)',
              height: 250,
              child: _buildTrendLineChart(
                provider.waterData.map((e) => e.conductivity).toList(),
                AppColors.info,
                'μS/cm',
              ),
            ),
            const SizedBox(height: 16),
            ChartCard(
              title: 'Peso de Tabletas (24h)',
              height: 250,
              child: _buildTrendLineChart(
                provider.tabletData.map((e) => e.weight).toList(),
                AppColors.success,
                'mg',
              ),
            ),
            const SizedBox(height: 16),
            ChartCard(
              title: 'Partículas Ambientales (24h)',
              height: 250,
              child: _buildTrendLineChart(
                provider.environmentData.map((e) => e.particles05.toDouble()).toList(),
                AppColors.warning,
                'partículas/m³',
              ),
            ),
            const SizedBox(height: 24),
            _buildSectionTitle('Análisis de Estacionalidad'),
            const SizedBox(height: 16),
            _buildSeasonalityAnalysis(),
          ],
        );
      },
    );
  }

  Widget _buildCorrelationTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildSectionTitle('Matriz de Correlación'),
        const SizedBox(height: 16),
        _buildCorrelationMatrix(),
        const SizedBox(height: 24),
        _buildSectionTitle('Scatter Plots'),
        const SizedBox(height: 16),
        _buildScatterPlots(),
        const SizedBox(height: 24),
        _buildSectionTitle('Análisis de Componentes'),
        const SizedBox(height: 16),
        _buildPCAAnalysis(),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: AppTextStyles.h3.copyWith(color: AppColors.textPrimary),
    );
  }

  Widget _buildStatsGrid(Map<String, dynamic> stats) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildStatBox('Total Registros', '${stats['totalRecords'] ?? 0}', Icons.data_usage),
        _buildStatBox('Anomalías', '${stats['anomalies'] ?? 0}', Icons.warning_amber),
        _buildStatBox('Tasa Anomalía', '${((stats['anomalyRate'] ?? 0) * 100).toStringAsFixed(1)}%', Icons.percent),
        _buildStatBox('Cumplimiento', '${((stats['compliance'] ?? 0) * 100).toStringAsFixed(1)}%', Icons.check_circle_outline),
      ],
    );
  }

  Widget _buildStatBox(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: AppColors.primary, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: AppTextStyles.h2.copyWith(color: AppColors.textPrimary),
          ),
          Text(
            label,
            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildDistributionChart(DataProvider provider) {
    return ChartCard(
      title: 'Distribución por Sistema',
      height: 200,
      child: PieChart(
        PieChartData(
          sections: [
            PieChartSectionData(
              value: provider.waterData.length.toDouble(),
              title: 'Agua\n${provider.waterData.length}',
              color: AppColors.info,
              radius: 60,
              titleStyle: AppTextStyles.caption.copyWith(color: Colors.white),
            ),
            PieChartSectionData(
              value: provider.tabletData.length.toDouble(),
              title: 'Tabletas\n${provider.tabletData.length}',
              color: AppColors.success,
              radius: 60,
              titleStyle: AppTextStyles.caption.copyWith(color: Colors.white),
            ),
            PieChartSectionData(
              value: provider.environmentData.length.toDouble(),
              title: 'Ambiente\n${provider.environmentData.length}',
              color: AppColors.warning,
              radius: 60,
              titleStyle: AppTextStyles.caption.copyWith(color: Colors.white),
            ),
          ],
          sectionsSpace: 2,
          centerSpaceRadius: 40,
        ),
      ),
    );
  }

  Widget _buildSystemComparison(DataProvider provider) {
    return ChartCard(
      title: 'Métricas Comparativas',
      height: 250,
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: 100,
          barGroups: [
            BarChartGroupData(x: 0, barRods: [
              BarChartRodData(toY: 95, color: AppColors.info, width: 20),
            ]),
            BarChartGroupData(x: 1, barRods: [
              BarChartRodData(toY: 92, color: AppColors.success, width: 20),
            ]),
            BarChartGroupData(x: 2, barRods: [
              BarChartRodData(toY: 88, color: AppColors.warning, width: 20),
            ]),
          ],
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  const titles = ['Agua', 'Tabletas', 'Ambiente'];
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      titles[value.toInt()],
                      style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                    ),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    '${value.toInt()}%',
                    style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: AppColors.border,
                strokeWidth: 1,
              );
            },
          ),
          borderData: FlBorderData(show: false),
        ),
      ),
    );
  }

  Widget _buildMLModelCard(
    String name,
    String description,
    double accuracy,
    double f1Score,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: AppTextStyles.h4.copyWith(color: AppColors.textPrimary),
                    ),
                    Text(
                      description,
                      style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildMetricBar('Accuracy', accuracy, color),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildMetricBar('F1-Score', f1Score, color),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricBar(String label, double value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
            ),
            Text(
              '${(value * 100).toStringAsFixed(1)}%',
              style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value,
            backgroundColor: AppColors.border,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Widget _buildROCCurve() {
    return ChartCard(
      title: 'Curva ROC - Ensemble',
      height: 300,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            getDrawingHorizontalLine: (value) => FlLine(
              color: AppColors.border,
              strokeWidth: 1,
            ),
            getDrawingVerticalLine: (value) => FlLine(
              color: AppColors.border,
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              axisNameWidget: Text(
                'Tasa de Falsos Positivos',
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toStringAsFixed(1),
                    style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              axisNameWidget: Text(
                'Tasa de Verdaderos Positivos',
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toStringAsFixed(1),
                    style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border.all(color: AppColors.border),
          ),
          minX: 0,
          maxX: 1,
          minY: 0,
          maxY: 1,
          lineBarsData: [
            // Diagonal (random classifier)
            LineChartBarData(
              spots: const [FlSpot(0, 0), FlSpot(1, 1)],
              isCurved: false,
              color: AppColors.textSecondary.withOpacity(0.5),
              dotData: const FlDotData(show: false),
              dashArray: [5, 5],
            ),
            // ROC curve
            LineChartBarData(
              spots: const [
                FlSpot(0, 0),
                FlSpot(0.05, 0.65),
                FlSpot(0.1, 0.80),
                FlSpot(0.15, 0.88),
                FlSpot(0.2, 0.92),
                FlSpot(0.3, 0.95),
                FlSpot(0.5, 0.98),
                FlSpot(1, 1),
              ],
              isCurved: true,
              color: AppColors.primary,
              barWidth: 3,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppColors.primary.withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConfusionMatrix() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(width: 80),
              Expanded(
                child: Text(
                  'Predicción',
                  style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              RotatedBox(
                quarterTurns: 3,
                child: Text(
                  'Real',
                  style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  children: [
                    Row(
                      children: [
                        const SizedBox(width: 60),
                        Expanded(
                          child: Text(
                            'Normal',
                            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        Expanded(
                          child: Text(
                            'Anomalía',
                            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        SizedBox(
                          width: 60,
                          child: Text(
                            'Normal',
                            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                          ),
                        ),
                        Expanded(child: _buildMatrixCell(847, AppColors.success, 'TN')),
                        const SizedBox(width: 4),
                        Expanded(child: _buildMatrixCell(23, AppColors.warning, 'FP')),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        SizedBox(
                          width: 60,
                          child: Text(
                            'Anomalía',
                            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                          ),
                        ),
                        Expanded(child: _buildMatrixCell(12, AppColors.error, 'FN')),
                        const SizedBox(width: 4),
                        Expanded(child: _buildMatrixCell(118, AppColors.primary, 'TP')),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildMetricChip('Precisión', '83.7%'),
              _buildMetricChip('Recall', '90.8%'),
              _buildMetricChip('F1', '87.1%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMatrixCell(int value, Color color, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Column(
        children: [
          Text(
            '$value',
            style: AppTextStyles.h3.copyWith(color: color),
          ),
          Text(
            label,
            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.primary.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(width: 4),
          Text(
            value,
            style: AppTextStyles.bodyBold.copyWith(color: AppColors.primary),
          ),
        ],
      ),
    );
  }

  Widget _buildTrendLineChart(List<double> data, Color color, String unit) {
    if (data.isEmpty) {
      return Center(
        child: Text(
          'Sin datos disponibles',
          style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
        ),
      );
    }

    final spots = data.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value);
    }).toList();

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          getDrawingHorizontalLine: (value) => FlLine(
            color: AppColors.border,
            strokeWidth: 1,
          ),
          drawVerticalLine: false,
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 50,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(1),
                  style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots.take(50).toList(),
            isCurved: true,
            color: color,
            barWidth: 2,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: color.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSeasonalityAnalysis() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Patrones Identificados',
            style: AppTextStyles.h4.copyWith(color: AppColors.textPrimary),
          ),
          const SizedBox(height: 16),
          _buildPatternItem(
            'Ciclo Diario',
            'Mayor actividad entre 8:00-18:00',
            Icons.wb_sunny_outlined,
            AppColors.warning,
          ),
          const SizedBox(height: 12),
          _buildPatternItem(
            'Ciclo Semanal',
            'Menor producción los fines de semana',
            Icons.calendar_today,
            AppColors.info,
          ),
          const SizedBox(height: 12),
          _buildPatternItem(
            'Tendencia Mensual',
            'Incremento gradual del 2.3% mensual',
            Icons.trending_up,
            AppColors.success,
          ),
        ],
      ),
    );
  }

  Widget _buildPatternItem(String title, String desc, IconData icon, Color color) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
              ),
              Text(
                desc,
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCorrelationMatrix() {
    final variables = ['Cond.', 'TOC', 'pH', 'Temp', 'Peso', 'Dureza'];
    final correlations = [
      [1.0, 0.72, 0.15, -0.23, 0.08, 0.12],
      [0.72, 1.0, 0.28, -0.18, 0.05, 0.09],
      [0.15, 0.28, 1.0, 0.45, -0.12, -0.08],
      [-0.23, -0.18, 0.45, 1.0, 0.35, 0.42],
      [0.08, 0.05, -0.12, 0.35, 1.0, 0.68],
      [0.12, 0.09, -0.08, 0.42, 0.68, 1.0],
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const SizedBox(width: 50),
              ...variables.map((v) => Expanded(
                child: Text(
                  v,
                  style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  textAlign: TextAlign.center,
                ),
              )),
            ],
          ),
          const SizedBox(height: 8),
          ...List.generate(variables.length, (i) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  SizedBox(
                    width: 50,
                    child: Text(
                      variables[i],
                      style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                    ),
                  ),
                  ...List.generate(variables.length, (j) {
                    final value = correlations[i][j];
                    return Expanded(
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        decoration: BoxDecoration(
                          color: _getCorrelationColor(value),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          value.toStringAsFixed(2),
                          style: AppTextStyles.caption.copyWith(
                            color: value.abs() > 0.5 ? Colors.white : AppColors.textPrimary,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    );
                  }),
                ],
              ),
            );
          }),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildLegendItem('-1.0', AppColors.error),
              const SizedBox(width: 8),
              _buildLegendItem('0', AppColors.border),
              const SizedBox(width: 8),
              _buildLegendItem('+1.0', AppColors.success),
            ],
          ),
        ],
      ),
    );
  }

  Color _getCorrelationColor(double value) {
    if (value > 0) {
      return AppColors.success.withOpacity(value.abs() * 0.8);
    } else if (value < 0) {
      return AppColors.error.withOpacity(value.abs() * 0.8);
    }
    return AppColors.border;
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
        ),
      ],
    );
  }

  Widget _buildScatterPlots() {
    return ChartCard(
      title: 'Peso vs Dureza (Tabletas)',
      height: 250,
      child: ScatterChart(
        ScatterChartData(
          scatterSpots: List.generate(50, (i) {
            return ScatterSpot(
              195 + (i % 10) + (i * 0.1),
              55 + (i % 15) + (i * 0.2),
              dotPainter: FlDotCirclePainter(
                radius: 4,
                color: i % 10 == 0 ? AppColors.error : AppColors.primary.withOpacity(0.6),
              ),
            );
          }),
          minX: 190,
          maxX: 210,
          minY: 50,
          maxY: 80,
          titlesData: FlTitlesData(
            show: true,
            bottomTitles: AxisTitles(
              axisNameWidget: Text(
                'Peso (mg)',
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              axisNameWidget: Text(
                'Dureza (N)',
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          gridData: FlGridData(
            show: true,
            getDrawingHorizontalLine: (value) => FlLine(
              color: AppColors.border,
              strokeWidth: 1,
            ),
            getDrawingVerticalLine: (value) => FlLine(
              color: AppColors.border,
              strokeWidth: 1,
            ),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border.all(color: AppColors.border),
          ),
        ),
      ),
    );
  }

  Widget _buildPCAAnalysis() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Varianza Explicada por Componente',
            style: AppTextStyles.h4.copyWith(color: AppColors.textPrimary),
          ),
          const SizedBox(height: 16),
          _buildPCABar('PC1', 0.45, '45%'),
          const SizedBox(height: 8),
          _buildPCABar('PC2', 0.28, '28%'),
          const SizedBox(height: 8),
          _buildPCABar('PC3', 0.15, '15%'),
          const SizedBox(height: 8),
          _buildPCABar('PC4', 0.08, '8%'),
          const SizedBox(height: 8),
          _buildPCABar('PC5', 0.04, '4%'),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.primary.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: AppColors.primary, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '3 componentes explican el 88% de la varianza total',
                    style: AppTextStyles.caption.copyWith(color: AppColors.textPrimary),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPCABar(String label, double value, String percentage) {
    return Row(
      children: [
        SizedBox(
          width: 40,
          child: Text(
            label,
            style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
          ),
        ),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: value,
              backgroundColor: AppColors.border,
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
              minHeight: 20,
            ),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 40,
          child: Text(
            percentage,
            style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }
}
