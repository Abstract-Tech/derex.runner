describe("Login tests", () => {
  const cms_url = Cypress.env("CMS_URL");
  it("user can not submit login form without entering username and password", () => {
    cy.visit(`${cms_url}/`);
    cy.get(".nav-not-signedin-signin > .action").click();
    cy.url().should("include", "/signin");
    cy.get("#email").clear(); // clear out username
    cy.get("#submit").click();
    cy.get("#login_error").should(
      "have.text",
      "Email or password is incorrect."
    );
  });

  it("user can not submit login form without entering username and password", () => {
    cy.visit(`${cms_url}/`);

    cy.get(".nav-not-signedin-signin > .action").click();
    cy.url().should("include", "/signin");
    cy.get("#email").type("foo@gmail.com"); // clear out username
    cy.get("#password").type("bar"); // clear out password
    cy.get("#submit").click();
    cy.get("#login_error").should(
      "have.text",
      "Email or password is incorrect."
    );
  });

  it("allows admin user access", () => {
    cy.visit(`${cms_url}/`);

    cy.get(".nav-not-signedin-signin > .action").click();
    cy.url().should("include", "/signin");
    cy.get("#email").type("staff@example.com");
    cy.get("#password").type("secret");
    cy.get("#submit").click();
  });
});
