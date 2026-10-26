const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { runInNewContext } = require("node:vm");
const ts = require("typescript");
const source = readFileSync(
  require("node:path").join(__dirname, "../src/lib/routing.ts"),
  "utf8",
);
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
  },
}).outputText;
const exportsObject = {};
runInNewContext(compiled, { exports: exportsObject });
const { homeFor, loginDestination, canAccessRoles } = exportsObject;
const user = (role) => ({
  id: 1,
  email: "test@example.com",
  role,
  is_active: true,
  is_superuser: false,
});
for (const [role, home] of [
  ["sdo", "/sdo"],
  ["office_staff", "/office"],
  ["meter_reader", "/reader"],
  ["consumer", "/consumer"],
]) {
  test(`${role} lands in its own workspace`, () =>
    assert.equal(homeFor(user(role)), home));
  test(`${role} ignores another workspace saved by login`, () =>
    assert.equal(
      loginDestination(user(role), home === "/office" ? "/sdo" : "/office"),
      home,
    ));
  test(`${role} restores a page in its own workspace`, () =>
    assert.equal(
      loginDestination(user(role), home + "/details?tab=1"),
      home + "/details?tab=1",
    ));
}
test("SDO cannot render the office dashboard", () =>
  assert.equal(canAccessRoles(user("sdo"), ["office_staff"]), false));
test("Office staff can render the office dashboard", () =>
  assert.equal(canAccessRoles(user("office_staff"), ["office_staff"]), true));
test("Superuser uses the SDO workspace", () => {
  const admin = { ...user(null), is_superuser: true };
  assert.equal(homeFor(admin), "/sdo");
  assert.equal(canAccessRoles(admin, ["office_staff"]), false);
  assert.equal(canAccessRoles(admin, ["sdo"]), true);
});
for (const destination of [
  "https://example.com",
  "//example.com",
  "/office",
  "/sdo-other",
  "/sdo/\\evil",
  "/sdo/\nother",
]) {
  test(`SDO rejects unsafe or unrelated destination ${JSON.stringify(destination)}`, () =>
    assert.equal(loginDestination(user("sdo"), destination), "/sdo"));
}
