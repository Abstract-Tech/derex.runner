describe("Knowledge Base Application", () => {
  // previous test omitted for brevity
  it("check for profile ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/");
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click({ force: true });
    });

    cy.get("#user-menu  .dropdown-item a[href$='/u/superuser']").then(
      ($button) => {
        cy.wrap($button).click({ force: true });
      }
    );

    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    cy.get("#user-menu  .dropdown-item a[href$='/account/settings']").then(
      ($button) => {
        cy.wrap($button).click({ force: true });
      }
    );
    cy.get("#u-field-select-year_of_birth").select("1988");
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    cy.get("#user-menu  .dropdown-item a[href$='/u/superuser']").then(
      ($button) => {
        cy.wrap($button).click({ force: true });
      }
    );
    cy.get(".profile-image-field > .u-field").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".clickable > .u-field-value-readonly").type("hi my name is test");
  });
});
