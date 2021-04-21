function randomString(length) {
  let result = "";
  let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

describe("Login tests", () => {
  beforeEach(() => {
    cy.visit(Cypress.env("LMS_URL"));
    cy.get(":nth-child(1) > :nth-child(2) > .sign-in-btn").click();
  });

  it("A user can't authenticate without submitting credentials", () => {
    cy.get("#login-email").clear();
    cy.get("#login-password").clear();
    cy.get(".action").click();
    cy.get(".message-copy > :nth-child(1)").should(
      "have.text",
      "Please enter your Email."
    );
    cy.get(".message-copy > :nth-child(2)").should(
      "have.text",
      "Please enter your Password."
    );
  });

  it("A user can't authenticate submitting wrong credentials", () => {
    cy.get("#login-email").type("foo@gmail.com");
    cy.get("#login-password").type("bar");
    cy.get(".action").click();
    cy.get(".message-copy > :nth-child(1)").should(
      "have.text",
      "Email or password is incorrect."
    );
  });

  it("A user can authenticate by submitting correct credentials", () => {
    cy.get("#login-email").type(Cypress.env("staff_user").email);
    cy.get("#login-password").type(Cypress.env("staff_user").password);
    cy.get(".action").click();
    cy.get(".username").should("have.text", Cypress.env("staff_user").username);
  });

  it("A user can reset his own password", () => {
    cy.get(".forgot-password").click();
    cy.get("#password-reset-email").type(Cypress.env("staff_user").email);
    cy.get("#password-reset > .action").click();
    cy.get(".js-password-reset-success").should("contain", "Check Your Email");
    cy.get(".js-password-reset-success").should(
      "contain",
      Cypress.env("staff_user").email
    );
  });

  it("An authenticated user can log out", () => {
    let account_api_url = `${Cypress.env("LMS_URL")}/api/user/v1/accounts`;
    cy.login_learner();
    cy.request(account_api_url).then((response) => {
      // Check that we are actually authenticated
      expect(response.status).to.eq(200);
    });
    cy.visit(Cypress.env("LMS_URL"));
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click({ force: true });
    });
    // Click the logout button
    cy.get("#user-menu > :nth-child(4) > a").click({ force: true });
    cy.request({ url: account_api_url, failOnStatusCode: false }).then(
      (response) => {
        // We should be logged out by now
        expect(response.status).to.eq(401);
      }
    );
  });
});

describe("Registration tests", () => {
  beforeEach(() => {
    cy.visit(Cypress.env("LMS_URL"));
    cy.get(":nth-child(1) > :nth-child(1) > .register-btn").click();
  });

  it("A unauthenticated user can register by filling the registration form", () => {
    cy.get("#register-name").type(`${randomString(10)} ${randomString(10)}`);
    cy.get("#register-username").type(randomString(10));
    cy.get("#register-email").type(`${randomString(10)}@example.com`);
    cy.get("#register-password").type("secret");
    cy.get(".action").click();
  });
});
