
describe("Landing Page", () => {

    const getLabelAndUrlsDict = (elems)=> {
        const names = [...elems].map(el => el.textContent.trim())
        const urls = [...elems].map(el => el.getAttribute('href'))
        return Object.assign({}, ...names.map((n, index) => ({ [n]: urls[index] })))
      }

      const getLogoAltAttributes = (logoContainer, attributeName, logoType)=> {
        // This function takes parent container name, logo type and attribute name
        // as parameter and return attribute value
 
        if (logoContainer =="header.global-header"){
            logoType = "/dashboard"
        return cy.get(logoContainer).find(`a[href="${logoType}"]>img`).invoke('attr', attributeName)
        
    }
        else{
            logoType = "/"
            return cy.get(logoContainer).find(`a[href="${logoType}"]>img`).invoke('attr', attributeName)
        }

        
      }


it('checks nav links in footer', function () {

    const expectedFooterNavLinks = {
        'About': '/about',
        'Blog': '/blog',
        "Contact": '/support/contact_us',
        "Donate":"/donate"
    }
    // Check for the presence of valid text and links in footer section
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));

    cy.visit("/dashboard");
    cy.get('footer .colophon .nav-colophon a').then((elems) => {
        const actualFooterNavLinks = getLabelAndUrlsDict(elems)
        expect(actualFooterNavLinks).to.deep.equal(expectedFooterNavLinks)
    })
})

it('checks logo information', function () {
    const edXlogoName = 'TestEdX Home Page'
    const edXlogoNameFooter = 'organization logo'

    // Check for log alt text and logo link in header
    // TODO: uncomment the next line once the logo alt issue is fixed
    getLogoAltAttributes('header.global-header', 'alt').should('eq', edXlogoName)
    // Check for logo alt text and logo link in footer
    getLogoAltAttributes('footer', 'alt').should('eq', edXlogoNameFooter)
  })

})