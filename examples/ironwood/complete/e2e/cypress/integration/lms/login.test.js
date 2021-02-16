describe("Login tests", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("user can not submit login form without entering username and password", () => {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.get("#login-email").clear(); // clear out username
    cy.get(".action").click();
    cy
    cy.get('.message-copy > :nth-child(1)')
      .should("have.text", "Please enter your Email.");
      
      cy.get('.message-copy > :nth-child(2)')
      .should("have.text", "Please enter your Password.");
      
  });

  it("user can not submit login form without entering username and password", () => {
    cy.visit(lms_url);
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#email").type("foo@gmail.com"); // clear out username
    cy.get("#password").type("bar"); // clear out password
    cy.get("#submit").click();
    cy
      .get(".message-copy")
      .should("have.text", "Email or password is incorrect.");
  });

  // it("allows admin user access", () => {
  //   cy.visit(lms_url);
  //   cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
  //   cy.url().should("include", "/login");
  //   cy.get("#email").type("staff@example.com");
  //   cy.get("#password").type("secret");
  //   cy.get("#submit").click();
  //   cy.url().should("include", "/dashboard");
  //   cy.contains("#main");
  // });
});
