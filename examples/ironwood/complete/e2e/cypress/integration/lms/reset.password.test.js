describe("Forget Password", () => {
  const lms_url = Cypress.env("LMS_URL");
  const mailslurper_url = Cypress.env("MAILSLURPER_URL");

  it("user can reset the password", () => {
    // Check what the last email is before this test runs
    let last_email;
    cy.request(mailslurper_url + "/mail").then((resp) => {
      last_email = resp.body.mailItems[0];
    });
    cy.visit(lms_url + "/login");
    cy.get("#forgot-password-link").click();
    cy.get("#pwd_reset_email").type("user@example.com");
    cy.get("#pwd_reset_button").click();
    cy.request(mailslurper_url + "/mail").then((resp) => {
      if (last_email == resp.body.mailItems[0]) {
        // Error: the email was not sent
        cy.fail(); // XXX Is this a method?
      }
      let body = resp.body.mailItems[0].body;
      let lms_host = lms_url.replace("https://", "");
      let url = body.match(lms_host + '[^ "]+')[0];
      cy.visit("https://" + url);
      cy.get("#new_password1").type("secret");
      cy.get("#new_password2").type("secret");
      cy.get(".action").click();
    });
  });
});
