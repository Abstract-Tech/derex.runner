describe("Registration Form", () => {

  const rand = (length, current) => {
    current = current ? current : "";
    return length
      ? rand(
          --length,
          "ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz".charAt(
            Math.floor(Math.random() * 60)
          ) + current
        )
      : current;
  };

  it("create new user", () => {
    cy.visit(`/`);
    cy.get(":nth-child(1) > :nth-child(1) > .register-btn").click();
    cy
      .get("#register-email")
      .should("have.attr", "name", "email")
      .type(`${rand(5)}@gmail.com`);
    cy
      .get("#register-name")
      .should("have.attr", "name", "name")
      .type("Foo bar");
    cy
      .get("#register-username")
      .should("have.attr", "name", "username")
      .type(`${rand(5)}`);
    cy
      .get("#register-password")
      .should("have.attr", "name", "password")
      .type("myname");

    cy.get(".action").click();
  });
});
