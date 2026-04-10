import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

import '../config/theme.dart';
import '../config/routes.dart';
import '../providers/alerts_provider.dart';

class MainShell extends StatefulWidget {
  final Widget child;
  
  const MainShell({super.key, required this.child});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;

  final List<_NavItem> _navItems = [
    _NavItem(
      icon: FontAwesomeIcons.gauge,
      label: 'Dashboard',
      route: AppRoutes.dashboard,
    ),
    _NavItem(
      icon: FontAwesomeIcons.droplet,
      label: 'Agua',
      route: AppRoutes.water,
    ),
    _NavItem(
      icon: FontAwesomeIcons.pills,
      label: 'Tabletas',
      route: AppRoutes.tablets,
    ),
    _NavItem(
      icon: FontAwesomeIcons.wind,
      label: 'Ambiente',
      route: AppRoutes.environment,
    ),
    _NavItem(
      icon: FontAwesomeIcons.bell,
      label: 'Alertas',
      route: AppRoutes.alerts,
    ),
    _NavItem(
      icon: FontAwesomeIcons.chartLine,
      label: 'Analytics',
      route: AppRoutes.analytics,
    ),
    _NavItem(
      icon: FontAwesomeIcons.gear,
      label: 'Config',
      route: AppRoutes.settings,
    ),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
    context.go(_navItems[index].route);
  }

  @override
  Widget build(BuildContext context) {
    final isDesktop = context.isDesktop;
    final isTablet = context.isTablet;
    
    return Scaffold(
      body: Row(
        children: [
          // Side navigation for desktop/tablet
          if (isDesktop || isTablet)
            _buildSideNav(isDesktop),
          
          // Main content
          Expanded(child: widget.child),
        ],
      ),
      
      // Bottom navigation for mobile
      bottomNavigationBar: (!isDesktop && !isTablet) 
          ? _buildBottomNav() 
          : null,
    );
  }

  Widget _buildSideNav(bool isExpanded) {
    return Container(
      width: isExpanded ? 220 : 72,
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(
          right: BorderSide(
            color: AppColors.border,
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          // Logo
          Container(
            height: 72,
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    FontAwesomeIcons.flask,
                    color: AppColors.background,
                    size: 18,
                  ),
                ),
                if (isExpanded) ...[
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'PharmaMon',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ],
            ),
          ),
          
          const Divider(color: AppColors.border, height: 1),
          
          // Nav items
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _navItems.length,
              itemBuilder: (context, index) {
                final item = _navItems[index];
                final isSelected = _selectedIndex == index;
                
                return _buildNavItem(
                  item: item,
                  isSelected: isSelected,
                  isExpanded: isExpanded,
                  index: index,
                );
              },
            ),
          ),
          
          // Status indicator
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: AppColors.success,
                    shape: BoxShape.circle,
                  ),
                ),
                if (isExpanded) ...[
                  const SizedBox(width: 8),
                  const Text(
                    'Sistema Activo',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.success,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem({
    required _NavItem item,
    required bool isSelected,
    required bool isExpanded,
    required int index,
  }) {
    return Consumer<AlertsProvider>(
      builder: (context, alertsProvider, _) {
        final showBadge = item.route == AppRoutes.alerts && 
            alertsProvider.unacknowledgedCount > 0;
        
        return Padding(
          padding: EdgeInsets.symmetric(
            horizontal: isExpanded ? 12 : 8,
            vertical: 4,
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => _onItemTapped(index),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: EdgeInsets.symmetric(
                  horizontal: isExpanded ? 16 : 0,
                  vertical: 12,
                ),
                decoration: BoxDecoration(
                  color: isSelected 
                      ? AppColors.primary.withValues(alpha: 0.1) 
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(12),
                  border: isSelected
                      ? Border.all(
                          color: AppColors.primary.withValues(alpha: 0.3),
                        )
                      : null,
                ),
                child: Row(
                  mainAxisAlignment: isExpanded 
                      ? MainAxisAlignment.start 
                      : MainAxisAlignment.center,
                  children: [
                    Stack(
                      clipBehavior: Clip.none,
                      children: [
                        FaIcon(
                          item.icon,
                          size: 18,
                          color: isSelected 
                              ? AppColors.primary 
                              : AppColors.textMuted,
                        ),
                        if (showBadge)
                          Positioned(
                            right: -6,
                            top: -6,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: const BoxDecoration(
                                color: AppColors.error,
                                shape: BoxShape.circle,
                              ),
                              child: Text(
                                alertsProvider.unacknowledgedCount.toString(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                    if (isExpanded) ...[
                      const SizedBox(width: 12),
                      Text(
                        item.label,
                        style: TextStyle(
                          color: isSelected 
                              ? AppColors.primary 
                              : AppColors.textSecondary,
                          fontWeight: isSelected 
                              ? FontWeight.w600 
                              : FontWeight.normal,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildBottomNav() {
    return Consumer<AlertsProvider>(
      builder: (context, alertsProvider, _) {
        return Container(
          decoration: const BoxDecoration(
            color: AppColors.surface,
            border: Border(
              top: BorderSide(color: AppColors.border, width: 1),
            ),
          ),
          child: SafeArea(
            child: SizedBox(
              height: 64,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: List.generate(_navItems.length, (index) {
                  final item = _navItems[index];
                  final isSelected = _selectedIndex == index;
                  final showBadge = item.route == AppRoutes.alerts && 
                      alertsProvider.unacknowledgedCount > 0;
                  
                  return InkWell(
                    onTap: () => _onItemTapped(index),
                    child: SizedBox(
                      width: 56,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Stack(
                            clipBehavior: Clip.none,
                            children: [
                              FaIcon(
                                item.icon,
                                size: 18,
                                color: isSelected 
                                    ? AppColors.primary 
                                    : AppColors.textMuted,
                              ),
                              if (showBadge)
                                Positioned(
                                  right: -8,
                                  top: -4,
                                  child: Container(
                                    padding: const EdgeInsets.all(4),
                                    decoration: const BoxDecoration(
                                      color: AppColors.error,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Text(
                                      alertsProvider.unacknowledgedCount.toString(),
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 8,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            item.label,
                            style: TextStyle(
                              fontSize: 10,
                              color: isSelected 
                                  ? AppColors.primary 
                                  : AppColors.textMuted,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _NavItem {
  final IconData icon;
  final String label;
  final String route;

  _NavItem({
    required this.icon,
    required this.label,
    required this.route,
  });
}
