describe("Account settings Page", () => {

  it("User can after the loged in navigate to the profile page", function () {

    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");

    cy.get(".toggle-user-dropdown").wait(2000).click();

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });

  });
});
