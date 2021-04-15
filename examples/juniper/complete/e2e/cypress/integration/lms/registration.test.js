describe("Registration", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("allows admin user access", () => {
    cy.visit(`${lms_url}/`);
    cy.get(":nth-child(1) > :nth-child(1) > .register-btn").click();
    cy.get("#register-email")
      .should("have.attr", "name", "email")
      .type("laythmassoud@gmail.com");
    cy.get("#register-name")
      .should("have.attr", "name", "name")
      .type("Foo bar");
    cy.get("#register-username")
      .should("have.attr", "name", "username")
      .type("abstract");
    cy.get("#register-password")
      .should("have.attr", "name", "password")
      .type("myname");
    // cy.get("#tos-yes").check();
    // cy.get("#honorcode-yes").check();
    cy.get(".action").click();
  });
});
