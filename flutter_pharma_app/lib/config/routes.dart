import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../screens/main_shell.dart';
import '../screens/dashboard/dashboard_screen.dart';
import '../screens/water/water_screen.dart';
import '../screens/tablets/tablets_screen.dart';
import '../screens/environment/environment_screen.dart';
import '../screens/alerts/alerts_screen.dart';
import '../screens/analytics/analytics_screen.dart';
import '../screens/settings/settings_screen.dart';

class AppRoutes {
  static const String dashboard = '/';
  static const String water = '/water';
  static const String tablets = '/tablets';
  static const String environment = '/environment';
  static const String alerts = '/alerts';
  static const String analytics = '/analytics';
  static const String settings = '/settings';

  static final GlobalKey<NavigatorState> _rootNavigatorKey = 
      GlobalKey<NavigatorState>(debugLabel: 'root');
  static final GlobalKey<NavigatorState> _shellNavigatorKey = 
      GlobalKey<NavigatorState>(debugLabel: 'shell');

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: dashboard,
    routes: [
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: dashboard,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const DashboardScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: water,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const WaterScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: tablets,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const TabletsScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: environment,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const EnvironmentScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: alerts,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const AlertsScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: analytics,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const AnalyticsScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
          GoRoute(
            path: settings,
            pageBuilder: (context, state) => CustomTransitionPage(
              key: state.pageKey,
              child: const SettingsScreen(),
              transitionsBuilder: _fadeTransition,
            ),
          ),
        ],
      ),
    ],
  );

  static Widget _fadeTransition(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: CurveTween(curve: Curves.easeInOut).animate(animation),
      child: child,
    );
  }
}
