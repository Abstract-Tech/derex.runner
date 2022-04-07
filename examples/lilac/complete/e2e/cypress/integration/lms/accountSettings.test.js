function randomString(length) {
  let result = "";
  let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

describe("Account settings tests", () => {
  beforeEach(() => {
    cy.login_learner();
    cy.visit("/");
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click({ force: true });
    });

    cy.get("#user-menu .dropdown-item a[href$='/account/settings']")
      .wait(1500)
      .click({ force: true });
  });

  it("Authenticated users can change their own profile full name", function () {
    cy.get("#field-input-name").clear().type(randomString(10));
  });

  it("Authenticated users can change their own profile date of birth", function () {
    let randomYear = String(Math.floor(Math.random() * (2021 - 1902) + 1902));
    cy.get("#u-field-select-year_of_birth").select(randomYear);
  });

  afterEach(() => {
    // We click somewhere else to trigger the save action
    cy.get("#u-field-value-username").click();
    cy.get("body").should(
      "contain",
      "Süççéss Ⱡ'σяєм ιρѕυм #Ýöür çhängés hävé ßéén sävéd. Ⱡ'σяєм ιρѕυм ∂σłσя ѕιт αмєт, ¢σηѕє¢#"
    );
  });
});
