# SEBMS Meter Scanner

Flutter Android/iOS source for field readers. Uses SEBMS's blue/gray interface style, camera capture, on-device Latin OCR, explicit field selection, editable verification, reading dates and authenticated Firestore submission. Manual entry is available when OCR fails. Photos stay on-device and are not uploaded.

## Existing backend contract

`core/services/firebase.py` reads document `meters/your_doc_id`, field `meter_list`:

```json
{"meter_list": [{"serial_no":12345,"reading":5678,"date":"2026-10-24"}]}
```

The app uses atomic `arrayUnion` with merge so concurrent submissions do not overwrite the array and retries of the same payload are deduplicated. It deliberately preserves the existing importer. The meter number must exist in Django. Different readings for the same meter/date can coexist in Firestore; Django skips subsequent meter/date entries. Correct already-imported values through the existing administrative workflow, not by resubmitting.

The single-document design inherits Firestore's document size limit and broad document access. It is a compatibility implementation, not a scalable per-reading schema. A future migration should use individual reading documents with assigned-reader rules and update the Django importer together.

## Build and configure

Flutter SDK is not installed in the authoring environment; analysis, widget tests, native compilation and device OCR have **not** been run. This directory contains app source, not an APK or generated native project.

1. Install a current stable Flutter SDK and native Android/iOS toolchains.
2. From this directory generate platform shells: `flutter create --platforms=android,ios --project-name sebms_scanner .`
3. Resolve packages with `flutter pub get`; review versions and commit `pubspec.lock` for reproducible builds. The manifest leaves package resolution to the installed SDK rather than claiming untested pinned versions.
4. Run `flutterfire configure` for the **same Firebase project** used by Django's service account. Add platform Firebase configurations. This source uses native `Firebase.initializeApp()`; ensure generated Android/iOS configurations are integrated. Never put the Django service-account private key in the app.
5. Enable Firebase Email/Password authentication and provision reader accounts. Django login credentials are not automatically Firebase accounts.
6. Configure Firestore rules in the Firebase console to permit only trusted provisioned readers to access this legacy document. Never enable public writes. For example use an admin-issued `meter_reader` custom claim; clients must not be able to assign it. Because the legacy array is shared, readers allowed to write can alter the entire document; migrate to per-reading records for stricter isolation.
7. Android: use the minimum/compile SDK required by the resolved ML Kit package (at least minSdk23), add INTERNET permission to the main manifest, and verify camera capture on a physical device. iOS: set the minimum target required by ML Kit and add `NSCameraUsageDescription` to Info.plist with `Capture electricity meters for SEBMS readings`.
8. Run `dart format lib test`, `flutter analyze`, `flutter test`, then `flutter run` on a physical device. Build with `flutter build apk` after verification.

## Acceptance checks

- Sign in using a provisioned reader; unauthorized accounts must fail Firestore writes.
- Scan a real meter: select serial and whole kWh reading from detected number chips, inspect the photograph, correct values, confirm and send.
- Cancel camera capture; deny camera permission; use manual input; retry a disconnected submission. Do not call a reading synced until the Firestore write completes.
- Verify the exact map in `meters/your_doc_id.meter_list`, then use SEBMS Fetch readings and verify the imported meter/date/value.
- Submit the identical payload twice and verify one array entry and one Django reading.
- Test multiple devices, unknown meters, invalid values and the administrative correction path before production.

No Firebase configuration, live writes, account creation, backend changes or production rule changes were performed while creating this source.
