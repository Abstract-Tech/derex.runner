describe("Login tests", () => {
  it("user can not submit login form without entering username and password", () => {
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#email").clear(); // clear out username
    cy.get("#submit").click();
    cy.get(".message-copy").should(
      "have.text",
      "Email or password is incorrect."
    );
  });

  it("user can not submit login form without entering username and password", () => {
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#email").type("foo@gmail.com"); // clear out username
    cy.get("#password").type("bar"); // clear out password
    cy.get("#submit").click();
    cy.get(".message-copy").should(
      "have.text",
      "Email or password is incorrect."
    );
  });

  it("allows admin user access", () => {
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
    cy.url().should("include", "/login");
    cy.get("#email").type("staff@example.com");
    cy.get("#password").type("secret");
    cy.get("#submit").click();
    cy.url().should("include", "/dashboard");
    cy.contains("#main");
  });
});
