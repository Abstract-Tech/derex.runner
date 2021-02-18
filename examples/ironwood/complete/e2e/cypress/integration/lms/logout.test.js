describe("Logout test ", () => {


  it("User can logout after logged in ", () => {

    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/")

    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });
    // click on the log out
    cy.get("#user-menu > :nth-child(4) > a").then(($button) => {
      cy.wrap($button).click({ force: true });
    });
  });
});
