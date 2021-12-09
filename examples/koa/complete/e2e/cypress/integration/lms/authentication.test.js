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
      "Pléäsé éntér ýöür Émäïl Ⱡ'σяєм ιρѕ#. Ⱡ'σяєм ιρѕυм ∂σłσя ѕιт αмєт, ¢#"
    );
    cy.get(".message-copy > :nth-child(2)").should(
      "have.text",
      "Pléäsé éntér ýöür Pässwörd Ⱡ'σяєм ιρѕυм ∂#. Ⱡ'σяєм ιρѕυм ∂σłσя ѕιт αмєт, ¢#"
    );
  });

  it("A user can't authenticate submitting wrong credentials", () => {
    cy.get("#login-email").type("foo@gmail.com");
    cy.get("#login-password").type("bar");
    cy.get(".action").click();
    cy.get(".message-copy > :nth-child(1)").should(
      "have.text",
      "Émäïl ör pässwörd ïs ïnçörréçt. Ⱡ'σяєм ιρѕυм ∂σłσя ѕιт αмєт, ¢σηѕє¢т#"
    );
  });

  it("A user can authenticate by submitting correct credentials", () => {
    cy.get("#login-email").type(Cypress.env("learner_user").email);
    cy.get("#login-password").type(Cypress.env("learner_user").password);
    cy.get(".action").click();
    cy.get(".username").should(
      "have.text",
      Cypress.env("learner_user").username
    );
  });

  it("A user can reset his own password", () => {
    cy.get(".login-help").click();
    cy.get("#login-help > .field-link").click();
    cy.get("#password-reset-email").type(Cypress.env("learner_user").email);
    cy.get("#password-reset > .action").click();
    cy.get(".js-password-reset-success").should(
      "contain",
      "Çhéçk Ýöür Émäïl Ⱡ'σяєм ιρѕυм ∂σłσя ѕιт αм#"
    );
    cy.get(".js-password-reset-success").should(
      "contain",
      Cypress.env("learner_user").email
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
    // The following click is needed to avoid the error
    // "element <input id="register-username" ...> is being covered by another element
    // `<label for="register-username" ...>`"
    cy.get(".text-username > .focus-out").click();
    cy.get("#register-username").type(randomString(10));
    cy.get("#register-email").type(`${randomString(10)}@example.com`);
    cy.get("#register-password").type("secret");
    cy.get(".action").click();
  });
});
