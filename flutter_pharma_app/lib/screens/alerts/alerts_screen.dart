import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';

import '../../config/theme.dart';
import '../../providers/alerts_provider.dart';
import '../../models/sensor_data.dart';

class AlertsScreen extends StatelessWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        title: const Text('Centro de Alertas'),
        actions: [
          Consumer<AlertsProvider>(
            builder: (context, provider, _) {
              return TextButton.icon(
                onPressed: provider.unacknowledgedCount > 0
                    ? () => provider.acknowledgeAllAlerts('Usuario')
                    : null,
                icon: const FaIcon(FontAwesomeIcons.check, size: 14),
                label: const Text('Reconocer Todas'),
              );
            },
          ),
        ],
      ),
      body: Consumer<AlertsProvider>(
        builder: (context, provider, _) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSummary(provider),
                const SizedBox(height: 24),
                _buildAlertsBySource(provider),
                const SizedBox(height: 24),
                _buildAlertsList(context, provider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSummary(AlertsProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            provider.criticalCount > 0 
                ? AppColors.error.withValues(alpha: 0.1) 
                : AppColors.success.withValues(alpha: 0.1),
            AppColors.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: provider.criticalCount > 0 
              ? AppColors.error.withValues(alpha: 0.3) 
              : AppColors.success.withValues(alpha: 0.3),
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem(
                'Total',
                provider.totalAlerts.toString(),
                FontAwesomeIcons.bell,
                AppColors.textPrimary,
              ),
              _buildSummaryItem(
                'Activas',
                provider.unacknowledgedCount.toString(),
                FontAwesomeIcons.triangleExclamation,
                AppColors.warning,
              ),
              _buildSummaryItem(
                'Criticas',
                provider.criticalCount.toString(),
                FontAwesomeIcons.circleExclamation,
                AppColors.error,
              ),
              _buildSummaryItem(
                'Monitoreo',
                provider.isMonitoring ? 'Activo' : 'Pausado',
                FontAwesomeIcons.eye,
                provider.isMonitoring ? AppColors.success : AppColors.textMuted,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    if (provider.isMonitoring) {
                      provider.stopMonitoring();
                    } else {
                      provider.startMonitoring();
                    }
                  },
                  icon: FaIcon(
                    provider.isMonitoring 
                        ? FontAwesomeIcons.pause 
                        : FontAwesomeIcons.play,
                    size: 14,
                  ),
                  label: Text(provider.isMonitoring ? 'Pausar' : 'Iniciar'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: provider.isMonitoring 
                        ? AppColors.warning 
                        : AppColors.success,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: provider.alerts.any((a) => a.isAcknowledged)
                      ? () => provider.clearAcknowledgedAlerts()
                      : null,
                  icon: const FaIcon(FontAwesomeIcons.trash, size: 14),
                  label: const Text('Limpiar'),
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.1, end: 0);
  }

  Widget _buildSummaryItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: FaIcon(icon, color: color, size: 18),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: AppColors.textMuted,
          ),
        ),
      ],
    );
  }

  Widget _buildAlertsBySource(AlertsProvider provider) {
    final bySource = provider.alertsBySource;
    final bySeverity = provider.alertsBySeverity;
    
    return Row(
      children: [
        Expanded(
          child: Container(
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
                  'Por Fuente',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                ...bySource.entries.map((entry) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          entry.key,
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          entry.value.toString(),
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
                if (bySource.isEmpty)
                  const Text(
                    'Sin alertas activas',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.textMuted,
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Container(
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
                  'Por Severidad',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                _buildSeverityRow('Critica', bySeverity[AlertSeverity.critical] ?? 0, AppColors.error),
                _buildSeverityRow('Mayor', bySeverity[AlertSeverity.major] ?? 0, AppColors.warning),
                _buildSeverityRow('Menor', bySeverity[AlertSeverity.minor] ?? 0, AppColors.info),
                _buildSeverityRow('Info', bySeverity[AlertSeverity.info] ?? 0, AppColors.textMuted),
              ],
            ),
          ),
        ),
      ],
    ).animate().fadeIn(delay: 100.ms);
  }

  Widget _buildSeverityRow(String label, int count, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          Text(
            count.toString(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertsList(BuildContext context, AlertsProvider provider) {
    final alerts = provider.alerts;
    
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
                'Historial de Alertas',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${alerts.length} alertas',
                style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (alerts.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Column(
                  children: [
                    FaIcon(
                      FontAwesomeIcons.bellSlash,
                      size: 32,
                      color: AppColors.textMuted,
                    ),
                    SizedBox(height: 12),
                    Text(
                      'No hay alertas registradas',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  ],
                ),
              ),
            )
          else
            ...alerts.asMap().entries.map((entry) {
              return _buildAlertItem(context, entry.value, provider)
                  .animate()
                  .fadeIn(delay: Duration(milliseconds: entry.key * 50));
            }),
        ],
      ),
    ).animate().fadeIn(delay: 200.ms);
  }

  Widget _buildAlertItem(BuildContext context, SystemAlert alert, AlertsProvider provider) {
    Color severityColor;
    IconData severityIcon;
    
    switch (alert.severity) {
      case AlertSeverity.critical:
        severityColor = AppColors.error;
        severityIcon = FontAwesomeIcons.circleExclamation;
        break;
      case AlertSeverity.major:
        severityColor = AppColors.warning;
        severityIcon = FontAwesomeIcons.triangleExclamation;
        break;
      case AlertSeverity.minor:
        severityColor = AppColors.info;
        severityIcon = FontAwesomeIcons.circleInfo;
        break;
      default:
        severityColor = AppColors.textMuted;
        severityIcon = FontAwesomeIcons.bell;
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: alert.isAcknowledged 
            ? AppColors.surfaceLight.withValues(alpha: 0.5) 
            : AppColors.surfaceLight,
        borderRadius: BorderRadius.circular(12),
        border: Border(
          left: BorderSide(color: severityColor, width: 4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              FaIcon(severityIcon, size: 14, color: severityColor),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  alert.message,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: alert.isAcknowledged 
                        ? AppColors.textMuted 
                        : AppColors.textPrimary,
                  ),
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
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                    color: severityColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${alert.source} | ${alert.parameter}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textMuted,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Valor: ${alert.currentValue.toStringAsFixed(2)} (Limite: ${alert.limitValue.toStringAsFixed(2)})',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    DateFormat('dd/MM HH:mm').format(alert.timestamp),
                    style: const TextStyle(
                      fontSize: 10,
                      color: AppColors.textMuted,
                    ),
                  ),
                  const SizedBox(height: 4),
                  if (alert.isAcknowledged)
                    Row(
                      children: [
                        const FaIcon(
                          FontAwesomeIcons.check,
                          size: 10,
                          color: AppColors.success,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          alert.acknowledgedBy ?? '',
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppColors.success,
                          ),
                        ),
                      ],
                    )
                  else
                    InkWell(
                      onTap: () => provider.acknowledgeAlert(alert.id, 'Usuario'),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'RECONOCER',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w600,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
