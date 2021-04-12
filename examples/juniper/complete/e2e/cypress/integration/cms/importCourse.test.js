describe("Studio home page", () => {
  const lms_url = Cypress.env("LMS_URL");
  const cms_url = Cypress.env("CMS_URL");
  

  it("test if an Admin able import course", async () => {
    cy.visit(lms_url);
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit(cms_url);
 
    cy.get("body").find("ul.list-courses").then(res => {
      if (res[0].children.length > 0) {
        cy.get(".course-item:last-child").click();
        cy.wait(2000)
        cy.get(".nav-course-tools > .title").click();
        cy.get(".nav-course-tools-import > a").click({ force: true });
        cy.wait(2000)
         cy.upload_file("courses/course.tar.gz");
         cy.get("#replace-courselike-button").wait(1000).click();
        cy.get("#view-updated-button").wait(10000).click();
      } else {
        cy.createCourse();
        cy.upload_file("#fileupload","courses/course.tar.gz");
        cy.get("#replace-courselike-button").wait(1000).click();
        cy.get("#view-updated-button").wait(10000).click();
      }
    });
  });
});
