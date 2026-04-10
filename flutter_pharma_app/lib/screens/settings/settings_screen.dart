import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/settings_provider.dart';
import '../../providers/data_provider.dart';
import '../../config/theme.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          'Configuración',
          style: AppTextStyles.h3.copyWith(color: AppColors.textPrimary),
        ),
        backgroundColor: AppColors.surface,
        elevation: 0,
      ),
      body: Consumer<SettingsProvider>(
        builder: (context, settings, _) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _buildSectionHeader('Apariencia'),
              _buildSettingCard([
                _buildSwitchTile(
                  'Modo Oscuro',
                  'Actualmente: ${settings.isDarkMode ? "Activado" : "Desactivado"}',
                  Icons.dark_mode,
                  settings.isDarkMode,
                  (value) => settings.toggleDarkMode(),
                ),
              ]),
              const SizedBox(height: 24),
              _buildSectionHeader('Notificaciones'),
              _buildSettingCard([
                _buildSwitchTile(
                  'Alertas Push',
                  'Recibir notificaciones de alertas críticas',
                  Icons.notifications_active,
                  settings.pushNotifications,
                  (value) => settings.togglePushNotifications(),
                ),
                const Divider(color: AppColors.border),
                _buildSwitchTile(
                  'Alertas por Email',
                  'Resumen diario de alertas',
                  Icons.email,
                  settings.emailAlerts,
                  (value) => settings.toggleEmailAlerts(),
                ),
                const Divider(color: AppColors.border),
                _buildSwitchTile(
                  'Sonido de Alerta',
                  'Reproducir sonido en alertas críticas',
                  Icons.volume_up,
                  settings.soundEnabled,
                  (value) => settings.toggleSound(),
                ),
              ]),
              const SizedBox(height: 24),
              _buildSectionHeader('Datos'),
              _buildSettingCard([
                _buildSliderTile(
                  'Intervalo de Actualización',
                  '${settings.refreshInterval} segundos',
                  Icons.refresh,
                  settings.refreshInterval.toDouble(),
                  5,
                  60,
                  (value) => settings.setRefreshInterval(value.round()),
                ),
                const Divider(color: AppColors.border),
                _buildActionTile(
                  'Limpiar Caché',
                  'Eliminar datos temporales',
                  Icons.cleaning_services,
                  () => _showClearCacheDialog(context),
                ),
                const Divider(color: AppColors.border),
                _buildActionTile(
                  'Exportar Datos',
                  'Descargar datos en CSV',
                  Icons.download,
                  () => _exportData(context),
                ),
              ]),
              const SizedBox(height: 24),
              _buildSectionHeader('Umbrales de Alerta'),
              _buildSettingCard([
                _buildThresholdTile(
                  'Conductividad Máx.',
                  'Sistema de agua',
                  Icons.water_drop,
                  '1.3 μS/cm',
                  AppColors.info,
                ),
                const Divider(color: AppColors.border),
                _buildThresholdTile(
                  'TOC Máximo',
                  'Carbono orgánico total',
                  Icons.science,
                  '500 ppb',
                  AppColors.warning,
                ),
                const Divider(color: AppColors.border),
                _buildThresholdTile(
                  'Peso de Tableta',
                  'Rango aceptable',
                  Icons.medication,
                  '190-210 mg',
                  AppColors.success,
                ),
                const Divider(color: AppColors.border),
                _buildThresholdTile(
                  'Partículas 0.5μm',
                  'Clase ISO 7',
                  Icons.blur_on,
                  '<352,000/m³',
                  AppColors.primary,
                ),
              ]),
              const SizedBox(height: 24),
              _buildSectionHeader('Modelos ML'),
              _buildSettingCard([
                _buildDropdownTile(
                  'Modelo Principal',
                  'Algoritmo de detección',
                  Icons.psychology,
                  settings.selectedModel,
                  ['Ensemble', 'Isolation Forest', 'LOF', 'One-Class SVM', 'Autoencoder'],
                  (value) => settings.setSelectedModel(value!),
                ),
                const Divider(color: AppColors.border),
                _buildSliderTile(
                  'Umbral de Anomalía',
                  '${(settings.anomalyThreshold * 100).toStringAsFixed(0)}%',
                  Icons.tune,
                  settings.anomalyThreshold,
                  0.5,
                  0.99,
                  (value) => settings.setAnomalyThreshold(value),
                ),
                const Divider(color: AppColors.border),
                _buildSwitchTile(
                  'Re-entrenamiento Auto',
                  'Actualizar modelos semanalmente',
                  Icons.autorenew,
                  settings.autoRetrain,
                  (value) => settings.toggleAutoRetrain(),
                ),
              ]),
              const SizedBox(height: 24),
              _buildSectionHeader('Información'),
              _buildSettingCard([
                _buildInfoTile(
                  'Versión',
                  '1.0.0 (Build 2024.01)',
                  Icons.info_outline,
                ),
                const Divider(color: AppColors.border),
                _buildInfoTile(
                  'Última Sincronización',
                  'Hace 5 minutos',
                  Icons.sync,
                ),
                const Divider(color: AppColors.border),
                _buildActionTile(
                  'Documentación',
                  'Ver guía de usuario',
                  Icons.menu_book,
                  () => _openDocumentation(context),
                ),
                const Divider(color: AppColors.border),
                _buildActionTile(
                  'Soporte Técnico',
                  'Contactar al equipo',
                  Icons.support_agent,
                  () => _contactSupport(context),
                ),
              ]),
              const SizedBox(height: 32),
              _buildDangerZone(context),
              const SizedBox(height: 32),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: AppTextStyles.h4.copyWith(color: AppColors.textPrimary),
      ),
    );
  }

  Widget _buildSettingCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildSwitchTile(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    Function(bool) onChanged,
  ) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppColors.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: AppColors.primary, size: 20),
      ),
      title: Text(
        title,
        style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
      ),
      subtitle: Text(
        subtitle,
        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
      ),
      trailing: Switch(
        value: value,
        onChanged: onChanged,
        activeColor: AppColors.primary,
      ),
    );
  }

  Widget _buildSliderTile(
    String title,
    String subtitle,
    IconData icon,
    double value,
    double min,
    double max,
    Function(double) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: AppColors.primary, size: 20),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
                    ),
                    Text(
                      subtitle,
                      style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SliderTheme(
            data: SliderThemeData(
              activeTrackColor: AppColors.primary,
              inactiveTrackColor: AppColors.border,
              thumbColor: AppColors.primary,
              overlayColor: AppColors.primary.withOpacity(0.2),
            ),
            child: Slider(
              value: value,
              min: min,
              max: max,
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionTile(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppColors.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: AppColors.primary, size: 20),
      ),
      title: Text(
        title,
        style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
      ),
      subtitle: Text(
        subtitle,
        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
      ),
      trailing: Icon(
        Icons.chevron_right,
        color: AppColors.textSecondary,
      ),
      onTap: onTap,
    );
  }

  Widget _buildThresholdTile(
    String title,
    String subtitle,
    IconData icon,
    String value,
    Color color,
  ) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(
        title,
        style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
      ),
      subtitle: Text(
        subtitle,
        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
      ),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Text(
          value,
          style: AppTextStyles.caption.copyWith(color: color),
        ),
      ),
    );
  }

  Widget _buildDropdownTile(
    String title,
    String subtitle,
    IconData icon,
    String value,
    List<String> options,
    Function(String?) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: AppColors.primary, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
                ),
                Text(
                  subtitle,
                  style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border),
            ),
            child: DropdownButton<String>(
              value: value,
              items: options.map((option) {
                return DropdownMenuItem(
                  value: option,
                  child: Text(
                    option,
                    style: AppTextStyles.caption.copyWith(color: AppColors.textPrimary),
                  ),
                );
              }).toList(),
              onChanged: onChanged,
              underline: const SizedBox(),
              dropdownColor: AppColors.surface,
              icon: Icon(Icons.arrow_drop_down, color: AppColors.textSecondary),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoTile(String title, String value, IconData icon) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppColors.textSecondary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: AppColors.textSecondary, size: 20),
      ),
      title: Text(
        title,
        style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
      ),
      trailing: Text(
        value,
        style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
      ),
    );
  }

  Widget _buildDangerZone(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.error.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.error.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber, color: AppColors.error, size: 20),
              const SizedBox(width: 8),
              Text(
                'Zona de Peligro',
                style: AppTextStyles.h4.copyWith(color: AppColors.error),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _showResetDialog(context),
              icon: const Icon(Icons.restart_alt),
              label: const Text('Restablecer Configuración'),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.error,
                side: BorderSide(color: AppColors.error),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: Text(
          'Limpiar Caché',
          style: AppTextStyles.h4.copyWith(color: AppColors.textPrimary),
        ),
        content: Text(
          '¿Estás seguro de que deseas eliminar los datos temporales? Esta acción no afectará tus configuraciones.',
          style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancelar',
              style: TextStyle(color: AppColors.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Caché limpiado correctamente'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
            ),
            child: const Text('Limpiar'),
          ),
        ],
      ),
    );
  }

  void _showResetDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: Text(
          'Restablecer Configuración',
          style: AppTextStyles.h4.copyWith(color: AppColors.error),
        ),
        content: Text(
          '¿Estás seguro? Esto restablecerá todas las configuraciones a sus valores predeterminados.',
          style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancelar',
              style: TextStyle(color: AppColors.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<SettingsProvider>().resetToDefaults();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Configuración restablecida'),
                  backgroundColor: AppColors.warning,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
            ),
            child: const Text('Restablecer'),
          ),
        ],
      ),
    );
  }

  void _exportData(BuildContext context) {
    final dataProvider = context.read<DataProvider>();
    // Simular exportación
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ),
            const SizedBox(width: 16),
            const Text('Exportando datos...'),
          ],
        ),
        backgroundColor: AppColors.info,
        duration: const Duration(seconds: 2),
      ),
    );
    
    Future.delayed(const Duration(seconds: 2), () {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Datos exportados correctamente'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    });
  }

  void _openDocumentation(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Abriendo documentación...'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _contactSupport(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.border,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Soporte Técnico',
              style: AppTextStyles.h3.copyWith(color: AppColors.textPrimary),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: Icon(Icons.email, color: AppColors.primary),
              title: Text(
                'soporte@pharmasystem.com',
                style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
              ),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: Icon(Icons.phone, color: AppColors.success),
              title: Text(
                '+1 (555) 123-4567',
                style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
              ),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: Icon(Icons.chat, color: AppColors.info),
              title: Text(
                'Chat en vivo',
                style: AppTextStyles.body.copyWith(color: AppColors.textPrimary),
              ),
              subtitle: Text(
                'Disponible 24/7',
                style: AppTextStyles.caption.copyWith(color: AppColors.textSecondary),
              ),
              onTap: () => Navigator.pop(context),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
