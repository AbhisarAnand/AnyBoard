import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '/Users/iprakharv/Desktop/AnyBoard_app_test/example/lib/main.dart';

void main() {
  testWidgets('Verify Platform version', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(MyApp());

    // Define the predicate for finding the Text widget containing the platform version.
    bool platformVersionPredicate(Widget widget) {
      if (widget is Text && widget.data != null) {
        return widget.data!.startsWith('Running on:');
      }
      return false;
    }

    // Verify that the platform version Text widget is found.
    expect(find.byWidgetPredicate(platformVersionPredicate), findsOneWidget);
  });
}
