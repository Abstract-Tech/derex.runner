describe("Forget Password", () => {
    const lms_url = Cypress.env("LMS_URL");
    it("user can reset the password", () => {
       cy.visit(lms_url)
       cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
       cy.get("#login-email").type();
        cy.get("#forgot-password-link").then($button => {
            cy.wrap($button).click();
        });
        cy.get("#pwd_reset_email").type("staff@example.com");
        cy.get("#pwd_reset_button").then($button => {
            cy.wrap($button).click();
        });
        cy.get(".icon").then($button => {
            cy.wrap($button).click();
        });
    });
});
