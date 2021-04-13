describe("Account settings Page", () => {
  it("User can after the loged in navigate to the profile page and change language, the date, delete the account", function() {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click({ force: true });
    });

    cy
      .get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

    cy.get("#u-field-select-pref-lang").select("en");
    cy.get("#u-field-select-year_of_birth").select("1990");
    cy.get("#delete-account-btn").click();
  });

})