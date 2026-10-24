# SDO-managed Android scanner accounts

The existing SDO Users form can create a Meter reader using an email and password. The backend creates a Firebase Auth identity with that same password, stores its UID in Django, and assigns the `meter_reader` custom claim. Other roles do not receive Firebase accounts.

Configure Firebase Admin on the backend before deploying this change:

- Project: `sebms-81d12` (same project as the Android scanner).
- Supply a server service-account certificate through the encrypted Render environment variable `FIREBASE_SERVICE_ACCOUNT_JSON`, or through a Render secret file and `FIREBASE_CREDENTIALS_PATH`.
- Keep the JSON private. Never commit it, add it to the Android app, expose it in a public variable, or paste it into chat.
- The service account needs Firebase Authentication user-management permissions and access to the existing Firestore meter document if ingestion is required. The Android public API key is not an Admin credential.
- Run the included migration before serving requests. The Render start script already runs migrations.

Existing reader passwords cannot be recovered from Django hashes. To enable scanner access for a pre-existing reader without a Firebase UID, explicitly set a new password via the SDO user-update API. An email already owned by an unlinked Firebase account returns a conflict; an administrator must verify ownership before linking or removing it.

Password, email, role, and active-status changes synchronize linked Firebase identities. Deleting a Django reader disables its Firebase identity rather than deleting Firebase audit history. Disabling/role removal/password change revokes refresh tokens; already-issued Firebase ID tokens can remain valid until expiry unless resource access also checks current authorization.

Firebase failure returns an actionable API error rather than silently creating a Django-only reader. New Firebase identities are removed when a subsequent Django write fails; if remote cleanup fails, logs identify the UID for reconciliation. Django and Firebase do not share a distributed transaction: connection loss during a remote operation or database commit failure still requires administrator reconciliation.

The existing Firestore rules were reported as public read/write during console inspection. This change does not replace live rules. Before operational use, restrict meter-document access to authorized readers and verify legacy-client compatibility. A Firebase identity alone does not protect public Firestore rules.

Verification before rollout:

1. Create a temporary reader through the authenticated SDO Users endpoint.
2. Sign in through Firebase using the same email/password; confirm its UID and reader claim.
3. Verify the scanner on a physical Android device with a non-production meter-reading test.
4. Disable the reader and verify subsequent Firebase sign-in is rejected.
5. Remove the temporary test account and any test readings.
