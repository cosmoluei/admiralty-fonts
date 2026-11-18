// swift-tools-version:5.7
// Admiralty fonts and symbols for iOS. Add this repository in Xcode (File > Add Package Dependencies).
import PackageDescription

let package = Package(
    name: "Admiralty",
    platforms: [.iOS(.v15)],
    products: [.library(name: "Admiralty", targets: ["Admiralty"])],
    targets: [
        .target(name: "Admiralty", path: "packages/ios/Admiralty/Sources/Admiralty",
                resources: [.copy("Fonts")])
    ]
)
