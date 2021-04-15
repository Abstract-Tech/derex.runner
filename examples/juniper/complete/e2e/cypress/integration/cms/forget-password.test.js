describe("Forget Password", () => {
  const cms_url = Cypress.env("CMS_URL");
  it("user can reset the password", () => {
    cy.visit(`${cms_url}/`);
    cy.get(".nav-not-signedin-signin > .action").click();
    cy.url().should("include", "/signin");
    cy.get("#email").type(Cypress.env("user_email"));
    // FIXME: the link points to the LMS
    //        cy.get(".action-forgotpassword").wait(1000).click();
    //        cy.get("#password-reset-email").type("staff@example.com");
    //        cy.get("#password-reset > .action").wait(2000).click();
    //        cy.get("#login-email").type(Cypress.env("user_email"));
    //        cy.get("#login-password").type(Cypress.env("user_password"));
    //        cy.get(".action").click();
  });
});
