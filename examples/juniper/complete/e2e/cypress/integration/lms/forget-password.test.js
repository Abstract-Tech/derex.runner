describe("Forget Password", () => {
    const lms_url = Cypress.env("LMS_URL");
    it("user can reset the password", () => {
       cy.visit(lms_url)
       cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
       cy.get("#login-email").type("staff@example.com");
        cy.get(".forgot-password").then($button => {
            cy.wrap($button).click();
        });
        cy.get("#password-reset-email").type("staff@example.com");
        cy.get("#password-reset > .action").then($button => {
            cy.wrap($button).click();
        });
    });
});
