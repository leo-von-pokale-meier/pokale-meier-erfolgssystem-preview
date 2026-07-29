const assert = require('node:assert/strict');
const test = require('node:test');
const {
  createWorkspace,
  createCustomer,
  activeCustomers,
  updateCustomer,
  createUser,
  can
} = require('./portal-core.js');

test('new internal workspace provides Admin, Designer and Berater roles', () => {
  const workspace = createWorkspace();

  assert.deepEqual(Object.keys(workspace.roles).sort(), ['admin', 'berater', 'designer']);
  assert.equal(workspace.users[0].role, 'admin');
  assert.equal(workspace.users[0].active, true);
});

test('active customer dashboard excludes paused and completed customer records', () => {
  const workspace = createWorkspace();
  createCustomer(workspace, { company: 'Muster GmbH', customerNumber: '10001' });
  createCustomer(workspace, { company: 'Pause KG', customerNumber: '10002', status: 'paused' });
  createCustomer(workspace, { company: 'Abschluss OHG', customerNumber: '10003', status: 'completed' });

  assert.deepEqual(activeCustomers(workspace).map((customer) => customer.company), ['Muster GmbH']);
});

test('customer detail persists JTL number, addresses, contacts and agreements separately', () => {
  const workspace = createWorkspace();
  const customer = createCustomer(workspace, { company: 'Impact Kunde GmbH', customerNumber: 'JTL-4729' });
  updateCustomer(workspace, customer.id, {
    contact: { name: 'Mara Mustermann', email: 'mara@example.test', phone: '0123 456' },
    deliveryAddress: { company: 'Impact Kunde GmbH', street: 'Lieferweg 12', postalCode: '50667', city: 'Köln', country: 'DE' },
    billingAddress: { company: 'Impact Kunde GmbH', street: 'Rechnungsweg 5', postalCode: '50668', city: 'Köln', country: 'DE' },
    agreement: { shippingMode: 'single', contact: 'Mara Mustermann', notes: 'Versand an einzelne Empfänger nach Freigabe.' }
  });

  assert.equal(customer.customerNumber, 'JTL-4729');
  assert.equal(customer.deliveryAddress.street, 'Lieferweg 12');
  assert.equal(customer.billingAddress.street, 'Rechnungsweg 5');
  assert.equal(customer.agreement.shippingMode, 'single');
  assert.equal(customer.contact.email, 'mara@example.test');
  assert.equal(customer.agreement.shippingMode, 'single');
});

test('only an Admin can manage users while Designer and Berater receive their intended rights', () => {
  const workspace = createWorkspace();
  const admin = workspace.users[0];
  const designer = createUser(workspace, admin.id, { name: 'Design Team', role: 'designer' });
  const berater = createUser(workspace, admin.id, { name: 'Beratung Team', role: 'berater' });

  assert.equal(can(workspace, admin.id, 'users.manage'), true);
  assert.equal(can(workspace, designer.id, 'users.manage'), false);
  assert.equal(can(workspace, designer.id, 'customers.write'), true);
  assert.equal(can(workspace, berater.id, 'agreements.write'), true);
  assert.throws(() => createUser(workspace, designer.id, { name: 'Nicht erlaubt', role: 'berater' }), /Berechtigung/);
});

test('the last active Admin cannot be demoted or deactivated', () => {
  const { updateUser } = require('./portal-core.js');
  const workspace = createWorkspace();
  const admin = workspace.users[0];

  assert.throws(() => updateUser(workspace, admin.id, admin.id, { role: 'designer' }), /Mindestens ein aktiver Admin/);
  assert.throws(() => updateUser(workspace, admin.id, admin.id, { active: false }), /Mindestens ein aktiver Admin/);
});
