import 'package:flutter/material.dart';
import '../config/theme.dart';

class StatusIndicator extends StatelessWidget {
  final bool isActive;
  final String label;

  const StatusIndicator({
    super.key,
    required this.isActive,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isActive 
            ? AppColors.success.withValues(alpha: 0.1) 
            : AppColors.textMuted.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isActive 
              ? AppColors.success.withValues(alpha: 0.3) 
              : AppColors.textMuted.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: isActive ? AppColors.success : AppColors.textMuted,
              shape: BoxShape.circle,
              boxShadow: isActive
                  ? [
                      BoxShadow(
                        color: AppColors.success.withValues(alpha: 0.4),
                        blurRadius: 8,
                        spreadRadius: 2,
                      ),
                    ]
                  : null,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: isActive ? AppColors.success : AppColors.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
