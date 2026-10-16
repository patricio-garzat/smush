import UIKit
import Capacitor
import WebKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Fuera del juego, iOS vuelve a apagar la pantalla como siempre
        UIApplication.shared.isIdleTimerDisabled = false
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
        disableZoom()
    }

    /// SMUSH! nunca hace zoom: ni con pellizco ni con doble toque.
    private func disableZoom() {
        guard let bridge = window?.rootViewController as? CAPBridgeViewController,
              let scrollView = bridge.webView?.scrollView else { return }
        scrollView.minimumZoomScale = 1
        scrollView.maximumZoomScale = 1
        scrollView.setZoomScale(1, animated: false)
        scrollView.pinchGestureRecognizer?.isEnabled = false
        scrollView.bouncesZoom = false
        // Es un juego: sin vista previa de links al dejar presionado
        bridge.webView?.allowsLinkPreview = false
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        // Called when the app was launched with a url. Feel free to add additional processing here,
        // but if you want the App API to support tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        // Called when the app was launched with an activity, including Universal Links.
        // Feel free to add additional processing here, but if you want the App API to support
        // tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }

}

/// La vista del juego: igual a la de Capacitor, pero el sonido puede empezar sin esperar un toque
/// (la intro de BluBer y la música del Inicio suenan desde que abre la app, como en cualquier juego).
class GameViewController: CAPBridgeViewController {
    override func webViewConfiguration(for instanceConfiguration: InstanceConfiguration) -> WKWebViewConfiguration {
        let config = super.webViewConfiguration(for: instanceConfiguration)
        config.mediaTypesRequiringUserActionForPlayback = []
        config.allowsInlineMediaPlayback = true
        // Pantalla encendida mientras juegas: el juego avisa con window.webkit.messageHandlers.keepAwake.postMessage(true/false)
        config.userContentController.add(KeepAwake(), name: "keepAwake")
        return config
    }
}

/// Mientras juegas, la pantalla no se oscurece ni se bloquea sola (el juego lo pide si tocaste en los últimos minutos)
class KeepAwake: NSObject, WKScriptMessageHandler {
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        let on = (message.body as? Bool) ?? false
        DispatchQueue.main.async { UIApplication.shared.isIdleTimerDisabled = on }
    }
}
