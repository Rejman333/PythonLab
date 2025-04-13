from pycluster.src.cli_parse import prepare_cli
from pycluster.src.img_procesing import ImgProcessor

def main():
    args = prepare_cli()
    print("I am working!")
    img_processor = ImgProcessor(args.filename)
    img_processor.create_clusters(args.gray, args.threshold)

    img_processor.draw_clusters_on_image(img_processor.img, img_processor.clusters, "data/results.jpg")
    img_processor.plot_clusters_on_img(img_processor.img, img_processor.clusters)
if __name__ == "__main__":
    main()
