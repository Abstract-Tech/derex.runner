describe("Logout test ", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("User can logout after logged in ", () => {
  
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#login-email").type("staff@example.com");
    cy.get("#login-password").type("secret");
    cy.get(".action").click();
    cy.url().should("include", "/");
       cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });
    // click the logout button
    cy.get('#user-menu > :nth-child(4) > a').click({ force: true });

    });

});
