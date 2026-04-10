import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../config/theme.dart';

enum TrendDirection { up, down, neutral }

class StatCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final IconData icon;
  final Color iconColor;
  final TrendDirection trend;

  const StatCard({
    super.key,
    required this.title,
    required this.value,
    required this.subtitle,
    required this.icon,
    required this.iconColor,
    this.trend = TrendDirection.neutral,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: FaIcon(
                    icon,
                    color: iconColor,
                    size: 16,
                  ),
                ),
              ),
              _buildTrendIcon(),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textMuted,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: const TextStyle(
              fontSize: 10,
              color: AppColors.textMuted,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildTrendIcon() {
    IconData trendIcon;
    Color trendColor;
    
    switch (trend) {
      case TrendDirection.up:
        trendIcon = FontAwesomeIcons.arrowTrendUp;
        trendColor = AppColors.success;
        break;
      case TrendDirection.down:
        trendIcon = FontAwesomeIcons.arrowTrendDown;
        trendColor = AppColors.error;
        break;
      case TrendDirection.neutral:
        trendIcon = FontAwesomeIcons.minus;
        trendColor = AppColors.textMuted;
        break;
    }
    
    return FaIcon(
      trendIcon,
      color: trendColor,
      size: 14,
    );
  }
}
