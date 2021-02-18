describe("Login tests", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("User can not logged in with empty username or password or both", () => {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.get("#login-email").clear(); // clear out username
    cy.get("#login-password").clear(); // clear out password
    cy.get(".action").click();
    cy.get('.message-copy > :nth-child(1)')
      .should("have.text", "Please enter your Email.");
      
      cy.get('.message-copy > :nth-child(2)')
      .should("have.text", "Please enter your Password.");
      
  });

  it("User can not logged in with wrong username or password or both ", () => {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#login-email").type("foo@gmail.com");
    cy.get("#login-password").type("bar");
    cy.get(".action").click();
    cy.get('.message-copy > :nth-child(1)')
      .should("have.text", "Email or password is incorrect.");
  });

  it("User can access with correct credentials", () => {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#login-email").type("staff@example.com");
    cy.get("#login-password").type("secret");
    cy.get(".action").click();
    cy.url().should("include", "/");
  });
});
