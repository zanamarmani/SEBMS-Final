import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sebms_scanner/main.dart';

void main() {
  testWidgets('Reader login conceals password and shows sign-in controls',
      (tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginPage()));
    expect(find.text('Reader email'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    final fields =
        tester.widgetList<TextField>(find.byType(TextField)).toList();
    expect(fields.length, 2);
    expect(fields.last.obscureText, isTrue);
  });
}
