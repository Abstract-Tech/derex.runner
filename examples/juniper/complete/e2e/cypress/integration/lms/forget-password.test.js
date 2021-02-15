/* describe("Forget Password", () => {
    beforeEach(() => {
        cy.visit("/");
    });

    it("user can reset the password", () => {
        cy.get("#email").type(Cypress.env("user_email"));
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
}); */
