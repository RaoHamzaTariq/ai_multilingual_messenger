import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:ai_multilingual_messenger/app.dart';
import 'package:ai_multilingual_messenger/providers/auth_provider.dart';
import 'package:ai_multilingual_messenger/providers/theme_provider.dart';

void main() {
  testWidgets('App launches and displays Splash Screen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => ThemeProvider()),
          ChangeNotifierProvider(create: (_) => AuthProvider()),
        ],
        child: const MyApp(),
      ),
    );

    await tester.pump();

    // Verify app title and splash screen components exist
    expect(find.text('AI Multilingual Messenger'), findsOneWidget);

    // Advance past the splash timer
    await tester.pump(const Duration(seconds: 2));
  });
}
