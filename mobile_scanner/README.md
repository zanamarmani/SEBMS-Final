# SEBMS Meter Scanner

Flutter Android/iOS source for field readers. Uses SEBMS's blue/gray interface style, camera capture, on-device Latin OCR, explicit field selection, editable verification, reading dates and authenticated Firestore submission. Manual entry is available when OCR fails. Photos stay on-device and are not uploaded.

## Existing backend contract

`core/services/firebase.py` reads document `meters/your_doc_id`, field `meter_list`:

```json
{"meter_list": [{"serial_no":12345,"reading":5678,"date":"2026-10-24"}]}
```

The app uses atomic `arrayUnion` with merge so concurrent submissions do not overwrite the array and retries of the same payload are deduplicated. It deliberately preserves the existing importer. The meter number must exist in Django. Different readings for the same meter/date can coexist in Firestore; Django skips subsequent meter/date entries. Correct already-imported values through the existing administrative workflow, not by resubmitting.

The single-document design inherits Firestore's document size limit and broad document access. It is a compatibility implementation, not a scalable per-reading schema. A future migration should use individual reading documents with assigned-reader rules and update the Django importer together.

## Android configuration and build

The generated Android project uses application ID `com.sebms.meter_scanner` and minSdk 23. Firebase Android client options are configured in `lib/firebase_options.dart` for project `sebms-81d12`, app ID `1:804634582053:android:0bd4e1338b9aa92f6c33cc`. These options contain a public client API key, never a service-account private key. Native `google-services.json` is not required because Firebase is initialized with explicit options.

Firebase Email/Password authentication was enabled on 2026-10-24. Reader accounts must be provisioned separately; Django accounts do not automatically exist in Firebase. No accounts were created during setup. The backend document contract remains `meters/your_doc_id.meter_list`; its exact live document must be verified before operational use.

Dependencies are pinned in `pubspec.yaml` and resolved in `pubspec.lock`. Install Flutter stable and Android SDK, then run:

```sh
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
```

The current build uses Android's debug signing configuration and is intended for device testing, not a production signing identity. Keep release signing keys outside Git.

Validation completed on 2026-10-24: Flutter analyzer reports no issues and all three automated tests pass (reading schema, invalid readings and login password concealment). Native APK compilation and physical-device Firebase/OCR verification are separate checks; do not infer them from Dart test success.

The Firebase console inspection reported public Firestore read/write rules. No rules were modified during setup. Restrict access to provisioned meter readers before operational rollout and verify existing client compatibility. Do not broaden access as a connection workaround.

## Acceptance checks

- Sign in using a provisioned reader; unauthorized accounts must fail Firestore writes.
- Scan a real meter: select serial and whole kWh reading from detected number chips, inspect the photograph, correct values, confirm and send.
- Cancel camera capture; deny camera permission; use manual input; retry a disconnected submission. Do not call a reading synced until the Firestore write completes.
- Verify the exact map in `meters/your_doc_id.meter_list`, then use SEBMS Fetch readings and verify the imported meter/date/value.
- Submit the identical payload twice and verify one array entry and one Django reading.
- Test multiple devices, unknown meters, invalid values and the administrative correction path before production.

Firebase Android registration and Email/Password provider setup were performed. No live meter writes, account creation, backend changes or production rule changes were performed.
