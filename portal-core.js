(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.PortalCore = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const roles = Object.freeze({
    admin: Object.freeze({ label: 'Admin', permissions: ['*'] }),
    designer: Object.freeze({ label: 'Designer', permissions: ['dashboard.read', 'customers.read', 'customers.write'] }),
    berater: Object.freeze({ label: 'Berater', permissions: ['dashboard.read', 'customers.read', 'customers.write', 'agreements.read', 'agreements.write', 'appointments.write'] })
  });

  const customerStatuses = Object.freeze(['active', 'paused', 'completed']);
  const shippingModes = Object.freeze(['single', 'collective', 'pickup', 'open']);
  const leaderboards = Object.freeze([
    Object.freeze({ id: 'monthly-orders', label: 'Kundenaufträge · Monat', period: 'month' }),
    Object.freeze({ id: 'yearly-orders', label: 'Kundenaufträge · Jahr', period: 'year' }),
    Object.freeze({ id: 'all-time-orders', label: 'Kundenaufträge · Gesamt', period: 'all' })
  ]);

  function gamificationConfig() {
    return {
      leaderboards: leaderboards.map((board) => ({ ...board })),
      unlockables: [
        { id: 'first-order', label: 'Erster Kundenauftrag', status: 'konzept' },
        { id: 'monthly-top3', label: 'Top 3 des Monats', status: 'konzept' },
        { id: 'yearly-top3', label: 'Top 3 des Jahres', status: 'konzept' }
      ]
    };
  }

  function text(value) {
    return typeof value === 'string' ? value.trim() : '';
  }

  function id(prefix) {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  }

  function blankAddress() {
    return { company: '', recipient: '', street: '', postalCode: '', city: '', country: 'DE' };
  }

  function blankContact() {
    return { name: '', role: '', email: '', phone: '' };
  }

  function blankAgreement() {
    return { shippingMode: 'open', contact: '', notes: '' };
  }

  function createWorkspace() {
    return {
      schemaVersion: 2,
      roles,
      users: [{ id: 'admin-local', name: 'Interne Administration', email: '', role: 'admin', active: true }],
      currentUserId: 'admin-local',
      customers: [],
      gamification: gamificationConfig()
    };
  }

  function userById(workspace, userId) {
    return workspace.users.find((user) => user.id === userId);
  }

  function can(workspace, userId, permission) {
    const user = userById(workspace, userId);
    if (!user || !user.active || !roles[user.role]) return false;
    const permissions = roles[user.role].permissions;
    return permissions.includes('*') || permissions.includes(permission);
  }

  function requirePermission(workspace, userId, permission) {
    if (!can(workspace, userId, permission)) throw new Error('Berechtigung fehlt.');
  }

  function validRole(role) {
    return Object.prototype.hasOwnProperty.call(roles, role);
  }

  function normalizeAddress(input) {
    const source = input && typeof input === 'object' ? input : {};
    return {
      company: text(source.company),
      recipient: text(source.recipient),
      street: text(source.street),
      postalCode: text(source.postalCode),
      city: text(source.city),
      country: text(source.country) || 'DE'
    };
  }

  function normalizeContact(input) {
    const source = input && typeof input === 'object' ? input : {};
    return { name: text(source.name), role: text(source.role), email: text(source.email), phone: text(source.phone) };
  }

  function normalizeAgreement(input) {
    const source = input && typeof input === 'object' ? input : {};
    return {
      shippingMode: shippingModes.includes(source.shippingMode) ? source.shippingMode : 'open',
      contact: text(source.contact),
      notes: text(source.notes)
    };
  }

  function createCustomer(workspace, input) {
    const source = input && typeof input === 'object' ? input : {};
    const company = text(source.company);
    const customerNumber = text(source.customerNumber);
    if (!company) throw new Error('Firmenname ist erforderlich.');
    if (!customerNumber) throw new Error('JTL-Kundennummer ist erforderlich.');
    if (workspace.customers.some((customer) => customer.customerNumber === customerNumber)) {
      throw new Error('Die JTL-Kundennummer existiert bereits.');
    }
    const customer = {
      id: id('customer'),
      company,
      customerNumber,
      status: customerStatuses.includes(source.status) ? source.status : 'active',
      miroBoardUrl: text(source.miroBoardUrl),
      contact: normalizeContact(source.contact),
      deliveryAddress: normalizeAddress(source.deliveryAddress),
      billingAddress: normalizeAddress(source.billingAddress),
      agreement: normalizeAgreement(source.agreement),
      nextStep: text(source.nextStep),
      internalNote: text(source.internalNote),
      salesAttribution: { ownerUserId: '', source: 'pending', orderIds: [] },
      updatedAt: new Date().toISOString()
    };
    workspace.customers.push(customer);
    return customer;
  }

  function updateCustomer(workspace, customerId, input) {
    const customer = workspace.customers.find((item) => item.id === customerId);
    if (!customer) throw new Error('Kunde wurde nicht gefunden.');
    const source = input && typeof input === 'object' ? input : {};
    if (Object.prototype.hasOwnProperty.call(source, 'company')) {
      const company = text(source.company);
      if (!company) throw new Error('Firmenname ist erforderlich.');
      customer.company = company;
    }
    if (Object.prototype.hasOwnProperty.call(source, 'customerNumber')) {
      const customerNumber = text(source.customerNumber);
      if (!customerNumber) throw new Error('JTL-Kundennummer ist erforderlich.');
      if (workspace.customers.some((item) => item.id !== customerId && item.customerNumber === customerNumber)) {
        throw new Error('Die JTL-Kundennummer existiert bereits.');
      }
      customer.customerNumber = customerNumber;
    }
    if (Object.prototype.hasOwnProperty.call(source, 'status') && customerStatuses.includes(source.status)) customer.status = source.status;
    if (Object.prototype.hasOwnProperty.call(source, 'miroBoardUrl')) customer.miroBoardUrl = text(source.miroBoardUrl);
    if (Object.prototype.hasOwnProperty.call(source, 'nextStep')) customer.nextStep = text(source.nextStep);
    if (Object.prototype.hasOwnProperty.call(source, 'internalNote')) customer.internalNote = text(source.internalNote);
    if (Object.prototype.hasOwnProperty.call(source, 'contact')) customer.contact = normalizeContact(source.contact);
    if (Object.prototype.hasOwnProperty.call(source, 'deliveryAddress')) customer.deliveryAddress = normalizeAddress(source.deliveryAddress);
    if (Object.prototype.hasOwnProperty.call(source, 'billingAddress')) customer.billingAddress = normalizeAddress(source.billingAddress);
    if (Object.prototype.hasOwnProperty.call(source, 'agreement')) customer.agreement = normalizeAgreement(source.agreement);
    customer.updatedAt = new Date().toISOString();
    return customer;
  }

  function activeCustomers(workspace) {
    return workspace.customers.filter((customer) => customer.status === 'active');
  }

  function createUser(workspace, actorId, input) {
    requirePermission(workspace, actorId, 'users.manage');
    const source = input && typeof input === 'object' ? input : {};
    const name = text(source.name);
    const role = text(source.role);
    if (!name) throw new Error('Name ist erforderlich.');
    if (!validRole(role)) throw new Error('Unbekannte Rolle.');
    const user = { id: id('user'), name, email: text(source.email), role, active: source.active !== false };
    workspace.users.push(user);
    return user;
  }

  function updateUser(workspace, actorId, userId, input) {
    requirePermission(workspace, actorId, 'users.manage');
    const user = userById(workspace, userId);
    if (!user) throw new Error('Benutzer wurde nicht gefunden.');
    const source = input && typeof input === 'object' ? input : {};
    const nextRole = Object.prototype.hasOwnProperty.call(source, 'role') ? source.role : user.role;
    const nextActive = Object.prototype.hasOwnProperty.call(source, 'active') ? Boolean(source.active) : user.active;
    if (!validRole(nextRole)) throw new Error('Unbekannte Rolle.');
    const otherActiveAdmins = workspace.users.filter((item) => item.active && item.role === 'admin' && item.id !== userId).length;
    if (user.active && user.role === 'admin' && !(nextActive && nextRole === 'admin') && otherActiveAdmins === 0) {
      throw new Error('Mindestens ein aktiver Admin ist erforderlich.');
    }
    if (Object.prototype.hasOwnProperty.call(source, 'name')) {
      const name = text(source.name);
      if (!name) throw new Error('Name ist erforderlich.');
      user.name = name;
    }
    if (Object.prototype.hasOwnProperty.call(source, 'email')) user.email = text(source.email);
    if (Object.prototype.hasOwnProperty.call(source, 'role')) user.role = nextRole;
    if (Object.prototype.hasOwnProperty.call(source, 'active')) user.active = nextActive;
    return user;
  }

  return {
    roles,
    customerStatuses,
    shippingModes,
    leaderboards,
    gamificationConfig,
    createWorkspace,
    createCustomer,
    updateCustomer,
    activeCustomers,
    createUser,
    updateUser,
    can,
    blankAddress,
    blankContact,
    blankAgreement
  };
}));
