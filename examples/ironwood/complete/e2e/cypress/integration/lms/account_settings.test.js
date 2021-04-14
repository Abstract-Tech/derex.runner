describe("Account settings Page", () => {
  it("User can after the loged in navigate to the profile page and change language", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").wait(2000).click();

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

    cy.get("#u-field-select-pref-lang").select("en");
  });

  it("User can after the loged in navigate to the profile page and change Date of birth", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").wait(2000).click();

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

    cy.get("#u-field-select-year_of_birth").select("1990");
  });

  it("User can after the loged in navigate to the profile page and delete the Account", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").wait(2000).click();

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

    cy.get("#delete-account-btn").click();
  });
});
